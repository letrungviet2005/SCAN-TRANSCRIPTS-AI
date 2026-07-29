import os

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import RESULTS_FOLDER, UPLOAD_FOLDER, ensure_directories
from pipeline import process_multiple_images_to_groups
from services.excel_exporter import export_to_excel

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER
ensure_directories()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/upload", methods=["POST"])
def upload_images():
    if "files" not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files selected"}), 400

    file_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_paths.append(file_path)

    if not file_paths:
        return jsonify({"error": "No valid files were uploaded"}), 400

    try:
        all_grouped_data, title_results, out_paths = process_multiple_images_to_groups(file_paths)
        excel_file_path = export_to_excel(all_grouped_data, app.config["RESULTS_FOLDER"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    response_data = {
        "title_results": title_results,
        "data": [
            {
                "image": f"/uploads/{os.path.basename(out_path)}",
                "list": grouped_rows,
            }
            for out_path, grouped_rows in zip(out_paths, all_grouped_data)
        ],
        "excel_download_link": f"/download/{os.path.basename(excel_file_path)}",
    }
    return jsonify(response_data)


@app.route("/uploads/<filename>", methods=["GET"])
def serve_uploaded_file(filename):
    try:
        return send_file(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    except Exception as exc:
        return jsonify({"error": f"File not found: {exc}"}), 404


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_file(os.path.join(app.config["RESULTS_FOLDER"], filename), as_attachment=True)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
