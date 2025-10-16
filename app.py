from flask import Flask, render_template, request, jsonify, Response
import os
from tools.data_ingestion.parser import handle_file_upload
from tools.context_management.context_handler import read_context, write_context, append_to_context
from tools.llm.cotas import cotas_stream

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "storage/session/data"

SESSION_PATH = "storage/session"
DATA_PATH = os.path.join(SESSION_PATH, "data")
CONTEXT_FILE = os.path.join(SESSION_PATH, "subjective-context.json")
METADATA_FILE = os.path.join(SESSION_PATH, "dataset-metadata.json")

# Ensure base session dirs exist at app start
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(os.path.join(SESSION_PATH, "scripts"), exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload-data", methods=["POST"])
def upload_data():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    meta = handle_file_upload(file, DATA_PATH, METADATA_FILE)
    return jsonify({"message": "File uploaded", "metadata": meta})

@app.route("/update-context", methods=["POST"])
def update_context():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "context must be a JSON object"}), 400
    write_context(CONTEXT_FILE, data)
    return jsonify({"message": "Context updated"})

@app.route("/generate-insights", methods=["POST"])
def generate_insights():
    def generate():
        for update in cotas_stream(SESSION_PATH, CONTEXT_FILE, METADATA_FILE, max_loops=20):
            # SSE-friendly payload
            yield f"data: {update}\n\n"
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
