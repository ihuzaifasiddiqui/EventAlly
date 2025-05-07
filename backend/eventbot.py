from flask import Flask, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import os

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)


app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route("/")
def hello_world():
    res = {'message' : "Hello from BE"}
    return jsonify(res)

@app.route("/upload", methods=["POST"])
def fileUpload():
    if request.method == "POST":
        if 'resume' not in request.files:
            return jsonify({"error": "No file found", "data": str(request.files)}), 400

        file = request.files['resume']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File successfully uploaded", "filename": filename})

app.run(debug=True)