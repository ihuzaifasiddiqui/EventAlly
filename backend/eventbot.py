from flask import Flask, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    res = {'message' : "Hello from BE", 'count' : 10}
    return jsonify(res)

app.run(debug=True)