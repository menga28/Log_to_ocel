import os
from werkzeug.utils import secure_filename
from flask import current_app


class FileService:
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower(
               ) in current_app.config['ALLOWED_EXTENSIONS']

    def save_file(self, file):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        return filepath
