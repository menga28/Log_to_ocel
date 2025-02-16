from flask import Blueprint, render_template, request, jsonify
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
    return render_template('index.html')


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file_service.allowed_file(file.filename):
        filepath = file_service.save_file(file)
        df = data_service.load_dataframe(filepath)
        if df is not None:
            stats = {
                "columns": list(df.columns),
                "data_types": df.dtypes.astype(str).to_dict()
            }
            return jsonify(stats)
        else:
            return jsonify({'error': data_service.error}), 400

    return jsonify({'error': 'Invalid file type'}), 400


@main_bp.route('/preview', methods=['GET'])
def get_preview():
    if data_service.df is None:
        return jsonify({"error": "No data loaded"}), 400

    preview_data = data_service.get_preview_data()
    return jsonify({
        "nested_columns": data_service.nested_columns,
        "preview_columns": preview_data['columns'],
        "sample_data": preview_data['data']
    })


@main_bp.route('/normalize', methods=['POST'])
def handle_normalization():
    try:
        indexes = request.json.get('indexes', [])
        data_service.normalize_data(indexes)

        if data_service.df_normalized is not None:
            normalized_columns = data_service.df_normalized.columns.tolist()
            logging.info("Normalization completed successfully")
            return jsonify({"message": "Normalization successful", "columns": normalized_columns}), 200
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
        logger.info("Setting OCEL parameters: activity=%s, timestamp=%s, object_types=%s, events_attrs=%s, object_attrs=%s",
                    activity, timestamp, object_types, events_attrs, object_attrs)
        data_service.set_ocel_parameters(
            activity, timestamp, object_types, events_attrs, object_attrs)
        data_service.o2o_enrichment()
        available_types = data_service.ocel.relations["ocel:type"].unique(
        ).tolist()
        available_activities = data_service.ocel.relations["ocel:activity"].unique(
        ).tolist()
        return jsonify({"message": "OCEL parameters set and OCEL created successfully",
                        "available_types": available_types,
                        "available_activities": available_activities}), 200
    except Exception as e:
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
        return jsonify({"message": "O2O Relationship qualifiers set successfully"}), 200
    except Exception as e:
        logger.error("Error setting O2O relationship qualifiers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@main_bp.route('/get_o2o_objects', methods=['GET'])
def get_o2o_objects():
    try:
        if data_service.ocel_o2o is None:
            logger.error("❌ O2O data not initialized")
            return jsonify({"error": "O2O data not available"}), 400

        logger.info(
            f"✅ O2O data found: {len(data_service.ocel_o2o.o2o)} relations")

        oids = data_service.ocel_o2o.o2o["ocel:oid"].unique().tolist()
        oids_2 = data_service.ocel_o2o.o2o["ocel:oid_2"].unique(
        ).tolist()

        logger.info(f"🔹 OIDs found: {oids}")
        logger.info(f"🔹 OIDs_2 found: {oids_2}")

        return jsonify({"oids": oids, "oids_2": oids_2}), 200
    except Exception as e:
        logger.error(f"❌ Error in get_o2o_objects: {e}")
        return jsonify({"error": str(e)}), 500
