from flask import Blueprint, render_template, request, jsonify
from app.services.file_service import FileService
from app.services.data_service import DataService
import os

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
        normalized_df = data_service.normalize_data(indexes)

        if normalized_df is not None:
            return jsonify({
                "columns": list(normalized_df.columns),
                "sample_data": normalized_df.head(20).to_dict('records')
            })
        return jsonify({"error": "Normalization failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
