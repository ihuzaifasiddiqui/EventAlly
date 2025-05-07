from flask import Flask, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import os
import json
import requests
import pytz

load_dotenv()

client = OpenAI(
    # api_key=os.environ.get("GEMINI_API_KEY"),
    # base_url="https://generativelanguage.googleapis.com/v1beta/"
)


app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

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

available_tools = {
    "get_current_time_ist": {
        "fn": get_current_time_ist,
        "description": "a tool to access the current time of specific timezone, so that user can know how much time is left for so and so event"
    },
    "submit_feedback_to_google_forms": {
        "fn": submit_feedback_to_google_forms,
        "description": "a feedbackBot, a tool that collects user feedback inputs of name, experience summary, and numerical rating (1-5)"
    }
}

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
    collect user feedback in 3 steps: name, experience summary, and numerical rating (1-5).
    Once all data is collected, call the `submit_feedback_to_google_forms` tool.

    Use friendly tone and confirm submissions clearly.

    Also you can use the current time to help users know what session is going on, when lunch is, or how much time is left.

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
        - submit_feedback_to_google_forms(name="Alice", experience="Great event!", rating=5): a feedbackBot, a tool that collects user feedback in steps of name, experience summary, and numerical rating (1-5)

    - If a function needs multiple inputs, return them as a JSON object inside "input". For example: {{ "step": "action", "function": "submit_feedback_to_google_forms", "input": {{ "name": "Ali", "experience": "Loved it!", "rating": 5 }} }}

    Example: 
        User query: What is the weather of chicago?
        Output: {{ "step": "plan", "content": "The user is interested in the weather of chicago" }}
        Output: {{ "step": "plan", "content": "From the available tools i should call the get_weather" }}
        Output: {{ "step": "action", "function": "get_weather", "input": "chicago" }}
        Output: {{ "step": "observe", "output": "12 degree celsius" }}
        Output: {{ "step": "output", "content": "The weather for chicago is 12 degree celsius" }}
"""


messages = [
    {"role": "system", "content": system_prompt},
]
while True: 
    user_query = input("> ")
    messages.append({"role": "user", "content": user_query})

    while True: 
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get('content')}")
            continue

        if parsed_output.get("step") == "action":
            tool_name =  parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if available_tools.get(tool_name, False) != False: 
                # output = available_tools[tool_name].get("fn")(tool_input)
                tool_fn = available_tools[tool_name]["fn"]
                if isinstance(tool_input, dict):
                    output = tool_fn(**tool_input)
                else:
                    output = tool_fn(tool_input)
                messages.append({ "role": "assistant", "content": json.dumps({"step": "observe", "output": output}) })
                continue

        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get('content')}")
            break

# @app.route("/")
# def hello_world():
#     res = {'message' : "Hello from BE"}
#     return jsonify(res)

# @app.route("/upload", methods=["POST"])
# def fileUpload():
#     if request.method == "POST":
#         if 'resume' not in request.files:
#             return jsonify({"error": "No file found", "data": str(request.files)}), 400

#         file = request.files['resume']

#         if file.filename == '':
#             return jsonify({"error": "Empty filename"}), 400

#         filename = secure_filename(file.filename)
#         print(filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return jsonify({"message": "File successfully uploaded", "filename": filename})

# app.run(debug=True)