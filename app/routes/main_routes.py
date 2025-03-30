from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.services.file_service import FileService
from app.services.data_service import DataService
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)
file_service = FileService()
data_service = DataService()


@main_bp.route('/')
def index():
    logger.info("Rendering index page")
    return render_template('index.html')


@main_bp.route('/load_sample', methods=['POST'])
def load_sample_data():
    logger.info("Load sample endpoint called")
    try:
        sample_filename = 'pancacke100txs.json'
        sample_filepath = os.path.join(
            current_app.static_folder, sample_filename)
        logger.info(f"Attempting to load sample file from: {sample_filepath}")

        if not os.path.exists(sample_filepath):
            logger.error(f"Sample file not found at: {sample_filepath}")
            return jsonify({'error': 'Sample file not found on server.'}), 404

        df = data_service.load_dataframe(sample_filepath)

        if df is not None:
            logger.info(
                f"Sample file '{sample_filename}' loaded successfully into DataService.")

            preview_data = data_service.get_preview_data()
            if preview_data:
                logger.info("Preview data for sample generated successfully.")

                return jsonify({
                    "message": "Sample loaded successfully",
                    "nested_columns": data_service.nested_columns,
                    "preview_columns": preview_data['columns'],
                    "sample_data": preview_data['data']
                }), 200
            else:
                logger.error(
                    "Failed to generate preview data after loading sample.")
                return jsonify({'error': 'Failed to generate preview data.'}), 500
        else:
            logger.error(
                f"Error loading sample DataFrame: {data_service.error}")
            return jsonify({'error': f"Failed to load sample data: {data_service.error}"}), 400

    except Exception as e:
        logger.error(
            f"Unexpected error in /load_sample: {str(e)}", exc_info=True)
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Upload endpoint called")
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    logger.info(f"Processing file: {file.filename}")
    if file and file_service.allowed_file(file.filename):
        filepath = file_service.save_file(file)
        logger.info(f"File saved at {filepath}")
        df = data_service.load_dataframe(filepath)
        if df is not None:
            stats = {
                "columns": list(df.columns),
                "data_types": df.dtypes.astype(str).to_dict()
            }
            logger.info(
                f"File processed successfully with {len(stats['columns'])} columns")
            return jsonify(stats)
        else:
            logger.error(f"Error loading DataFrame: {data_service.error}")
            return jsonify({'error': data_service.error}), 400

    logger.error("Invalid file type")
    return jsonify({'error': 'Invalid file type'}), 400


@main_bp.route('/preview', methods=['GET'])
def get_preview():
    logger.info("Preview endpoint called")
    if data_service.df is None:
        logger.warning("No data loaded for preview (df is None)") 
        return jsonify({"error": "No data loaded. Please upload a file or load the sample first."}), 400

    preview_data = data_service.get_preview_data()
    if preview_data:
        logger.info("Preview data retrieved successfully")
        return jsonify({
            "nested_columns": data_service.nested_columns,
            "preview_columns": preview_data['columns'],
            "sample_data": preview_data['data']
        })
    else:
        logger.error("Failed to get preview data even though df exists.")
        return jsonify({"error": "Failed to retrieve preview data."}), 500



@main_bp.route('/normalize', methods=['POST'])
def handle_normalization():
    try:
        indexes = request.json.get('indexes', [])
        logger.info(f"⚙️ Normalization started for indexes: {indexes}")
        data_service.normalize_data(indexes)

        if data_service.df_normalized is not None:
            normalized_columns = data_service.df_normalized.columns.tolist()
            logger.info(
                f"Normalization completed successfully. Columns: {normalized_columns}")
            return jsonify({"message": "Normalization successful", "columns": normalized_columns}), 200

        logger.error("Normalization failed")
        return jsonify({"error": "Normalization failed"}), 400

    except Exception as e:
        logger.error(f"Error during normalization: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route('/set_ocel_parameters', methods=['POST'])
def set_ocel_parameters():
    try:
        activity = request.json.get('activity')
        timestamp = request.json.get('timestamp')
        object_types = request.json.get('object_types', [])
        events_attrs = request.json.get('events_attrs', [])
        object_attrs = request.json.get('object_attrs', [])
        logger.info(
            f"⚙️ Setting OCEL parameters: activity={activity}, timestamp={timestamp}, object_types={object_types}")

        data_service.set_ocel_parameters(
            activity, timestamp, object_types, events_attrs, object_attrs)
        logger.info("OCEL parameters set successfully")

        data_service.o2o_enrichment()
        logger.info("🔗 O2O enrichment completed")

        available_types = data_service.ocel.relations["ocel:type"].unique(
        ).tolist()
        available_activities = data_service.ocel.relations["ocel:activity"].unique(
        ).tolist()

        return jsonify({"message": "OCEL parameters set and OCEL created successfully",
                        "available_types": available_types,
                        "available_activities": available_activities}), 200
    except Exception as e:
        logger.error(f"Error in set_ocel_parameters: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route('/set_e2o_relationship_qualifiers', methods=['POST'])
def set_e2o_relationship_qualifiers():
    try:
        qualifier_map = request.json.get('qualifier_map', {})
        logger.info("Received qualifier map: %s", qualifier_map)
        data_service.set_e2o_relationship_qualifiers(qualifier_map)
        return jsonify({"message": "Relationship qualifiers set successfully"}), 200
    except Exception as e:
        logger.error("Error setting relationship qualifiers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@main_bp.route('/set_o2o_relationship_qualifiers', methods=['POST'])
def set_o2o_relationship_qualifiers():
    try:
        qualifier_map = request.json.get('qualifier_map', {})
        logger.info("Received O2O qualifier map: %s", qualifier_map)
        data_service.set_o2o_relationship_qualifiers(qualifier_map)

        # Supponiamo che data_service.save_file abbia salvato il file OCEL aggiornato
        # nel percorso corrente con nome "ocel_o2o_qualifiers.jsonocel".
        file_name = "ocel_o2o_qualifiers.jsonocel"
        file_path = os.path.join(os.getcwd(), file_name)
        logger.info("Sending updated OCEL file from %s", file_path)

        # Restituisco il file come attachment; il browser lo scaricherà con il nome "ocel_updated.jsonocel"
        return send_file(file_path, as_attachment=True, download_name="ocel_updated.jsonocel")
    except Exception as e:
        logger.error("Error setting O2O relationship qualifiers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@main_bp.route('/get_o2o_objects', methods=['GET'])
def get_o2o_objects():
    try:
        if data_service.ocel_o2o is None:
            logger.error("O2O data not initialized")
            return jsonify({"error": "O2O data not available"}), 400

        logger.info(
            f"O2O data found: {len(data_service.ocel_o2o.o2o)} relations")

        oids = data_service.ocel_o2o.o2o["ocel:oid"].unique().tolist()
        oids_2 = data_service.ocel_o2o.o2o["ocel:oid_2"].unique(
        ).tolist()

        logger.info(f"🔹 OIDs found: {oids}")
        logger.info(f"🔹 OIDs_2 found: {oids_2}")

        return jsonify({"oids": oids, "oids_2": oids_2}), 200
    except Exception as e:
        logger.error(f"Error in get_o2o_objects: {e}")
        return jsonify({"error": str(e)}), 500
