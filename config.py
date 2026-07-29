import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
PROCESSED_IMAGES_FOLDER = os.path.join(ROOT_DIR, "processed_images")
RESULTS_FOLDER = os.path.join(ROOT_DIR, "results_excel")


def ensure_directories():
    for folder in (UPLOAD_FOLDER, PROCESSED_IMAGES_FOLDER, RESULTS_FOLDER):
        os.makedirs(folder, exist_ok=True)
