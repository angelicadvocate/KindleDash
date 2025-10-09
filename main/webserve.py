import os
from flask import Flask, send_file, send_from_directory
from pathlib import Path

app = Flask(__name__)

# Paths
CONFIGURATOR_DIR = Path(__file__).resolve().parent.parent / "configurator"
CURRENT_IMAGE_DIR = Path(__file__).resolve().parent.parent / "current_image"
CURRENT_IMAGE_FILE = CURRENT_IMAGE_DIR / "currentimage.png"

@app.route("/configurator/<path:filename>")
def configurator_files(filename):
    return send_from_directory(CONFIGURATOR_DIR, filename)

@app.route("/")
def configurator_index():
    return send_from_directory(CONFIGURATOR_DIR, "config_index.html")

@app.route("/slides")
def serve_slide():
    if CURRENT_IMAGE_FILE.exists():
        return send_file(CURRENT_IMAGE_FILE, mimetype="image/png")
    return "No slide available", 404

if __name__ == "__main__":
    # Run Flask app in the main process
    app.run(host="0.0.0.0", port=5000)
