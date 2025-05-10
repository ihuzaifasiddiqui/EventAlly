from flask import Flask, jsonify, request
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import os
import json
import requests
import pytz
import fitz
import hashlib
import numpy as np

from qdrant_client import QdrantClient, models

load_dotenv()

# Configure Gemini API
configure(api_key=os.environ.get("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "resumes"

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Initialize Gemini models
embedding_model = GenerativeModel("embedding-001")
chat_model = GenerativeModel("gemini-1.5-flash")  # You can also use "gemini-2.0-flash" if available

# Ensure the Qdrant collection exists
def create_qdrant_collection():
    collections = qdrant_client.get_collections().collections
    if QDRANT_COLLECTION_NAME not in [col.name for col in collections]:
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),  # Gemini embeddings are 768 dimensions
        )

create_qdrant_collection()

def get_all_attendees_qdrant():
    """Get a list of all attendees from Qdrant."""
    points = qdrant_client.scroll(
        collection_name=QDRANT_COLLECTION_NAME,
        scroll_filter=None,
        limit=10000,
        with_payload=True
    )
    user_ids = set()
    for point in points[0]:
        if point.payload and 'user_id' in point.payload:
            user_ids.add(point.payload['user_id'])
    return list(user_ids)

def search_resume_qdrant(query, user_id=None):
    """Search for information in resumes using Qdrant."""
    try:
        # Get embeddings using Gemini instead of OpenAI
        response = embedding_model.embed_content(
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = response.embedding
        
        search_filter = None
        if user_id:
            search_filter = models.Filter(must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))])

        search_results = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=5,
            with_payload=True
        )

        results = []
        for hit in search_results:
            payload = hit.payload
            if payload:
                results.append(f"Name: {payload.get('name', 'N/A')}, Summary: {payload.get('text_sample', 'N/A')[:200]}...")
        return "\n".join(results)
    except Exception as e:
        return f"Error searching resumes: {str(e)}"

def get_current_time_ist(_input=None):
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        return now.strftime("%Y-%m-%d %H:%M:%S")

def submit_feedback_to_google_forms(name, experience, rating):
    print("🔨Tool called: submit_feedback_to_google_forms")
    form_post_url = 'https://docs.google.com/forms/d/e/1FAIpQLSefrkNNYydNTp-hQwBapGP1lg1uZP8G2ghSE5GSeaNere06Tw/formResponse'
    form_data = {
        "entry.1274867366": name,
        "entry.1546935728": experience,
        "entry.1774645751": rating
    }
    try:
        res = requests.post(form_post_url, data=form_data)
        print(res.content)
        return "✅ Feedback submitted successfully!" if res.status_code == 200 else "❌ Failed to submit feedback."
    except Exception as e:
        return f"❌ Error submitting feedback: {e}"


system_prompt = f"""
    Hey you are a helpful, user friendly AI assistant, you will help workshop participants with
    useful, real-time information, who is specific to a responding to user queries regarding a meetup happening at ScaleOrange technologies
    Masthan Nagar, Kavuri Hills, Madhapur, Hyderabad, Telangana 500081, India
    About Event
        Build with AI - A Workshop in Collaboration with Google for Developers

        Happening on: Sunday, May 18, 2025 from 10:00 AM IST to 4:00 PM IST

        Hyderabad's developer community is invited to an experiential 1 day workshop on Artificial Intelligence (AI). This hands-on event, hosted in collaboration with Google for Developers, brings together industry experts, innovators, and aspiring AI practitioners.

        Who Should Attend

        - Developers & Engineers
        - Tech Professionals
        - Students & Recent Graduates
        - Entrepreneurs & Product Managers

    Agenda of the event/workshop
        10:00 - 11:00 AM: Hands On Workshop: Automation using Claude and MCP Server
        - Vijender P, Alumnx
        11:00 - 12:00 PM: Hands On Workshop: Agentic AI - Jitendra Gupta (Google
        Developer Expert)
        12:00 - 1:00 PM: Industry Connect Session - Ravi Babu, Apex Cura Healthcare
        1:00 - 2:00 PM: Lunch
        2:00 - 3:00 PM: Hands On Workshop: Build an Event Bot using RAG - Vishvas
        Dubey, TCS
        3:00 - 3:30 PM: Industry Application of AI: Building Multi AI Agents - Surendranath
        Reddy, QAPilot
        3:30 - 4:00 PM: Workshop: Building Multi AI Agents - Mahidhar, NexusHub

    If the user wants to give feedback, act as a feedback bot as well
    collect user feedback in 2 steps: experience summary, and numerical rating (1-5), we already have user's name, so use that.
    Once all data is collected, call the `submit_feedback_to_google_forms` tool.

    Use friendly tone and confirm submissions clearly.

    Also you can use the current time to help users know what session is going on, when lunch is, or how much time is left.
    Don't leave the user with no response, you're there to help them - highly important

    For example
    You are working with a Qdrant vector database containing information about event attendees. Each entry has a 'user_id', 'name', and a 'text_sample' of their resume.

    Rules:
    - Follow the output JSON format
    - Always perform one step at a time and wait for the next input
    - Carefully analyze the user query

    Output JSON format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of the function if the step is function",
        "input": "The input parameter for the function",
    }}

    Available tools:
        - get_current_time_ist: a tool to access the current time of specific timezone, so that user can know how much time is left for so and so event.
        - submit_feedback_to_google_forms(name="Alice", experience="Great event!", rating=5): a feedbackBot, a tool that collects user feedback in steps of name, experience summary, and numerical rating (1-5), this will ask back to back 3 questions to the user and done, it will not divert in between
        - search_resume_qdrant(query, user_id=None): a tool to search for information in resumes based on the provided query, optionally for a specific user ID
    - If a function needs multiple inputs, return them as a JSON object inside "input". For example: {{ "step": "action", "function": "submit_feedback_to_google_forms", "input": {{ "name": "Ali", "experience": "Loved it!", "rating": 5 }} }}

    Feedback Flow Rules:
        - When user says "I want to give feedback", set `feedback_in_progress` to true and begin the flow.
        - While `feedback_in_progress` is true:
            1. Do not respond with any other information (e.g., resume results).
            2. Collect the following in order:
                - experience and rating
            3. Once these 2 fields are collected:
                - Call `submit_feedback_to_google_forms` with the collected data
                - Clear `feedback_data`
        - Always acknowledge with a friendly message after each step.
        - Never return resume results when `feedback_in_progress` is true, even if the user's name matches a resume entry.

    If the user inputs their own name (e.g., when asking about resumes), always pass their `user_id` in the `search_resume_qdrant` tool so they don't receive results about themselves.

    Rules:
        - Never ever send an error response 500 or related to it, be always positive, you can do it, be in the context of this event.
        - Whatever it be, but don't spread false information, don't make up things when you don't know
    
    Example:
        User query: What is the weather of chicago?
        Output: {{ "step": "plan", "content": "The user is interested in the weather of chicago" }}
        Output: {{ "step": "plan", "content": "From the available tools i should call the get_weather" }}
        Output: {{ "step": "action", "function": "get_weather", "input": "chicago" }}
        Output: {{ "step": "observe", "output": "12 degree celsius" }}
        Output: {{ "step": "output", "content": "The weather for chicago is 12 degree celsius" }}
"""


@app.route("/")
def hello_world():
    res = {'message' : "Hello from BE with Qdrant (Gemini version)"}
    return jsonify(res)

@app.route("/upload", methods=["POST"])
def fileUpload():
    if request.method == "POST":
        print("Upload request received")

        name = request.form.get("name")
        if not name:
            return jsonify({"error": "Name is required"}), 400

        if 'resume' not in request.files:
            print("No resume file found in request:", request.files)
            return jsonify({"error": "No file found", "data": str(request.files)}), 400

        file = request.files['resume']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        print(f"Processing file: {filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # STEP 1: Extract text from PDF
            resume_text = ""
            try:
                with fitz.open(file_path) as doc:
                    resume_text = "\n".join(page.get_text() for page in doc)
                    print(f"Successfully extracted {len(resume_text)} characters from PDF")
            except Exception as pdf_error:
                print(f"Error extracting PDF text: {pdf_error}")
                return jsonify({"error": "Failed to read PDF", "details": str(pdf_error)}), 500

            if not resume_text.strip():
                print("Warning: Extracted text is empty")
                return jsonify({"error": "Failed to extract text from resume"}), 500

            print(f"Extracted resume text sample: {resume_text[:200]}...")

            # STEP 2: Store in Qdrant using Gemini embeddings
            try:
                user_id = name.lower().strip().replace(" ", "_")
                
                # Get embeddings using Gemini instead of OpenAI
                embedding_response = embedding_model.embed_content(
                    content=resume_text,
                    task_type="retrieval_document"
                )
                embedding = embedding_response.embedding

                qdrant_client.upsert(
                    collection_name=QDRANT_COLLECTION_NAME,
                    points=[
                        models.PointStruct(
                            id=int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16),
                            vector=embedding,
                            payload={
                                "user_id": user_id,
                                "name": name,
                                "filename": filename,
                                "text_sample": resume_text[:1000],
                                "upload_time": datetime.now().isoformat()
                            }
                        )
                    ]
                )
                print(f"Successfully added resume to Qdrant for user: {user_id}")
                return jsonify({
                    "message": "Resume stored successfully in Qdrant",
                    "filename": filename,
                    "name": name,
                    "user_id": user_id
                })

            except Exception as qdrant_error:
                print(f"Error adding to Qdrant: {qdrant_error}")
                return jsonify({"error": "Failed to store in Qdrant", "details": str(qdrant_error)}), 500

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"General error processing resume: {e}")
            return jsonify({"error": "Failed to process resume", "details": str(e)}), 500
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed temporary file: {file_path}")


@app.route("/chat", methods=["POST"])
def chatting():
    
    available_tools = {
        "get_current_time_ist": {
            "fn": get_current_time_ist,
            "description": "a tool to access the current time of specific timezone, so that user can know how much time is left for so and so event"
        },
        "submit_feedback_to_google_forms": {
            "fn": submit_feedback_to_google_forms,
            "description": "a feedbackBot, a tool that collects user feedback inputs of name (user_id), experience summary, and numerical rating (1-5)"
        },
        "search_resume_qdrant": {
            "fn": search_resume_qdrant,
            "description": "Searches for a person's resume information based on the provided query and user ID."
        }
    }

    # Get all attendees for context from Qdrant
    try:
        attendees = get_all_attendees_qdrant()
        attendees_str = ", ".join(attendees)
    except Exception as e:
        print(f"Error getting attendees from Qdrant: {e}")
        attendees_str = "Could not retrieve attendee list"
    
    current_user = request.json.get("user", "").strip()  # 👈 Receive current user

    final_prompt = f"""
        {system_prompt}

        The current user interacting is: {current_user}.

        Here is the list of attendees at the event: {attendees_str}. You can use the 'search_resume_qdrant' tool to find information about them if needed. Remember not to disclose personal contact information.
        
        The current user interacting is: {current_user}.
        You already know the current user's name — avoid asking it again unless you're unsure.
        If the user wants to submit feedback, collect ONLY the rating (1-5) and a short experience summary.
        Once both are collected, automatically use the `submit_feedback_to_google_forms` tool using:
        - name = {current_user}
        - rating = (from user input)
        - summary = (from user input)
    """

    chat_memory = [
        {"role": "user", "parts": [final_prompt]}
    ]

    user_query = request.json.get("message", "").strip()

    if not user_query:
        return jsonify({"error": "Missing message"}), 400

    chat_memory.append({"role": "model", "parts": ["I'll help workshop participants with information about the event."]})
    chat_memory.append({"role": "user", "parts": [user_query]})

    while True:
        try:
            response = chat_model.generate_content(
                chat_memory,
                generation_config={
                    "response_mime_type": "application/json"
                }
            )

            # Extract and parse the JSON response
            try:
                parsed_output = json.loads(response.text)
                chat_memory.append({"role": "model", "parts": [json.dumps(parsed_output)]})

                if parsed_output.get("step") == "plan":
                    print(f"🧠: {parsed_output.get('content')}")
                    continue

                if parsed_output.get("step") == "action":
                    tool_name = parsed_output.get("function")
                    tool_input = parsed_output.get("input")

                    if available_tools.get(tool_name):
                        tool_fn = available_tools[tool_name]["fn"]
                        if isinstance(tool_input, dict):
                            output = tool_fn(**tool_input)
                        else:
                            output = tool_fn(tool_input)
                        chat_memory.append({"role": "model", "parts": [json.dumps({"step": "observe", "output": output})]})
                        continue

                if parsed_output.get("step") == "output":
                    print(f"🤖: {parsed_output.get('content')}")
                    return jsonify({"message": parsed_output.get("content")})

            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}, Content: {response.text}")
                return jsonify({"error": "Failed to parse AI response"}), 500

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True)