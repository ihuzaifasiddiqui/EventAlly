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
import fitz

from mem0 import Memory
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from langchain.tools import tool

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI


load_dotenv()

client = OpenAI(
    # api_key=os.environ.get("GEMINI_API_KEY"),
    # base_url="https://generativelanguage.googleapis.com/v1beta/"
)


app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
QDRANT_HOST = "localhost"

config = {
    "version" : "v1.1",
    "embedder" : {
        "provider" : "openai",
        "config" : {"api_key" : os.environ.get("OPENAI_API_KEY"), "model" : "text-embedding-3-small"}
    },
    "llm" : {"provider" : "openai", "config" : {"api_key" : os.environ.get("OPENAI_API_KEY"), "model" : "gpt-4o"}},
    "vector_store" : {
        "provider" : "qdrant",
        "config" : {
            "host" : QDRANT_HOST,
            "port" : 6333
        }
    },
    "graph_store" : {
        "provider" : "neo4j",
        "config" : {"url": os.environ.get("NEO4J_URL"), "username" : os.environ.get("NEO4J_USERNAME"), "password" : os.environ.get("NEO4J_PASSWORD")}
    }
}

mem_client = Memory.from_config(config)
qdrant_client = QdrantClient(host="localhost", port=6333)


# Neo4j Connection
graph = Neo4jGraph(
    url="bolt://localhost:7687",  # Neo4j local host URL
    username="neo4j",
    password=os.environ.get("NEO4J_PASSWORD")  # Ensure this password is stored in your environment variables
)

# Refresh schema (optional, but good for understanding node/relationship structure)
graph.refresh_schema()

# Create the QA Chain (for querying the Neo4j graph)
cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-4o"),
    qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    validate_cypher=True,
    verbose=True,
    allow_dangerous_requests=True
)

# Initialize the Neo4j driver
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.environ.get("NEO4J_PASSWORD")))

def fetch_relationships():
    with driver.session() as session:
        result = session.run("MATCH p=()-[r]->() RETURN p LIMIT 10000")
        relationships = []
        for record in result:
            path = record["p"]
            for rel in path.relationships:
                relationships.append({
                    "start_node": dict(rel.start_node.items()),
                    "end_node": dict(rel.end_node.items()),
                    "type": rel.type,
                    "properties": dict(rel.items())
                })
        return relationships

def get_all_attendees():
    """Get a list of all attendees from the database"""
    # Retrieve all points from the 'memories' collection
    points = qdrant_client.scroll(collection_name="mem0", scroll_filter=None, limit=10000)
    
    # Extract unique user_ids from the payloads
    user_ids = set()
    for point in points[0]:
        payload = point.payload
        if 'user_id' in payload:
            user_ids.add(payload['user_id'])
    
    return list(user_ids)

def search_resume(query, user_id=None):
    """
    Search for information in resumes based on the provided query
    
    Args:
        query (str): The question or search query
        user_id (str, optional): The specific user ID to search for. If None, search all users
        
    Returns:
        str: The search results
    """
    try:
        # If a specific user_id is provided, search only their information
        if user_id:
            search_result = mem_client.search(
                query=query,
                user_id=user_id,
                limit=5
            )
            return f"Information about {user_id}: {search_result}"
        
        # Otherwise, search across all user memories
        else:
            # Get all attendee user IDs
            attendees = get_all_attendees()
            
            # Initialize results
            all_results = []
            
            # Search for each attendee
            for attendee in attendees:
                search_result = mem_client.search(
                    query=query,
                    user_id=attendee,
                    limit=3
                )
                
                if search_result and len(search_result) > 0:
                    # Format the results to avoid exposing sensitive information
                    formatted_result = {
                        "name": attendee,
                        "info": [item for item in search_result if not any(sensitive in str(item).lower() for sensitive in ["phone", "mobile", "email", "address", "personal"])]
                    }
                    all_results.append(formatted_result)
            
            # Use Neo4j for more structured queries
            neo4j_query = f"""
            MATCH (p:Person)-[r]->(n)
            WHERE toLower(toString(p)) CONTAINS toLower('{query}') 
               OR toLower(toString(n)) CONTAINS toLower('{query}')
               OR toLower(toString(r)) CONTAINS toLower('{query}')
            RETURN p.name as Name, TYPE(r) as Relationship, n as Related
            LIMIT 10
            """
            
            try:
                with driver.session() as session:
                    neo_result = session.run(neo4j_query).data()
                    if neo_result:
                        all_results.append({"neo4j_results": neo_result})
            except Exception as e:
                all_results.append({"neo4j_error": str(e)})
            
            # If no results, try the cypher chain
            if not all_results or len(all_results) == 0:
                try:
                    cypher_result = cypher_chain.run(query)
                    all_results.append({"cypher_result": cypher_result})
                except Exception as e:
                    all_results.append({"cypher_error": str(e)})
            
            # Format the result as a string
            return json.dumps(all_results, indent=2)
    
    except Exception as e:
        return f"Error searching resumes: {str(e)}"

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
    Don't leave the user with no response, you're there to help them - highly important

    For example
    You are working with a Neo4j graph database. The schema includes:
        - Node labels: Person, Company
        - Properties for Person: user_id, name, skills, email
        - Properties for Company: name, industry
        - Relationship types: WORKS_AT, KNOWS

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
        - search_resume(query, user_id=None): a tool to search for information in resumes based on the provided query, optionally for a specific user ID
    - If a function needs multiple inputs, return them as a JSON object inside "input". For example: {{ "step": "action", "function": "submit_feedback_to_google_forms", "input": {{ "name": "Ali", "experience": "Loved it!", "rating": 5 }} }}
    
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
    res = {'message' : "Hello from BE"}
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
            
            # STEP 2: Store knowledge into Neo4j via mem0
            try:
                print("Sending resume to mem0 for processing...")
                system_message = "You are an extractor that turns resumes into structured graph facts. Extract key information like name, email, phone, skills, education, projects, and connect them as a knowledge graph."
                
                # Ensure user_id is properly formatted
                user_id = name.lower().strip().replace(" ", "_")
                
                res = mem_client.add(
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": resume_text}
                    ],
                    user_id=user_id,
                    metadata={"filename": filename, "upload_time": datetime.now().isoformat()}
                )
                print(f"Mem0 add response: {res}")
                
                # Verify data was added by checking if we can retrieve it
                verification = mem_client.search(
                    query="basic information",
                    user_id=user_id,
                    limit=1
                )
                print(f"Verification search result: {verification}")
                
                # Directly add to Qdrant as a backup
                try:
                    # Get or create collection
                    collections = qdrant_client.get_collections()
                    if "resumes" not in [col.name for col in collections.collections]:
                        qdrant_client.create_collection(
                            collection_name="resumes",
                            vectors_config={"size": 768, "distance": "Cosine"}
                        )
                    
                    # Generate a simple embedding for the resume
                    # We're using a simplified approach here - in production you'd use a proper embedding
                    import hashlib
                    import numpy as np
                    resume_hash = hashlib.md5(resume_text.encode()).hexdigest()
                    pseudo_embedding = np.zeros(768)
                    for i, char in enumerate(resume_hash):
                        if i < 768:
                            pseudo_embedding[i] = ord(char) / 255.0
                    
                    # Store in Qdrant
                    qdrant_client.upsert(
                        collection_name="resumes",
                        points=[{
                            "id": int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16),
                            "vector": pseudo_embedding.tolist(),
                            "payload": {
                                "user_id": user_id,
                                "name": name,
                                "filename": filename,
                                "text_sample": resume_text[:1000],
                                "upload_time": datetime.now().isoformat()
                            }
                        }]
                    )
                    print(f"Successfully added resume directly to Qdrant")
                except Exception as qdrant_error:
                    print(f"Error adding directly to Qdrant: {qdrant_error}")
                
                return jsonify({
                    "message": "Resume stored successfully", 
                    "filename": filename, 
                    "name": name,
                    "user_id": user_id,
                    "mem0_response": str(res)
                })
                
            except Exception as mem0_error:
                print(f"Error with mem0 client: {mem0_error}")
                return jsonify({"error": "Failed to store in knowledge graph", "details": str(mem0_error)}), 500

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
        },
        "search_resume": {
            "fn": search_resume,
            "description": "Searches for a person's resume information based on the provided query and user ID."
        }
    }

    # Get relationship data for enhancing the prompt
    try:
        relationships = fetch_relationships()
    except Exception as e:
        print(f"Error fetching relationships: {e}")
        relationships = []

    # Get all attendees for context
    try:
        attendees = get_all_attendees()
        attendees_str = ", ".join(attendees)
    except Exception as e:
        print(f"Error getting attendees: {e}")
        attendees_str = "Could not retrieve attendee list"

    final_prompt = f"""
        {system_prompt}

        here is the memory of all the users present in the event, don't disclose their personal info such as mobile numbers etc, just share their professional info with others when asked, this is a big responsibility in your hands
        If user asks about any other user if he/she is attending this event or present at this event, then search them in this memories, if you find them then respond according to their query.

        Event attendees: {attendees_str}
    """

    chat_memory = [
        {"role": "system", "content": final_prompt}
    ]

    user_query = request.json.get("message", "").strip()

    if not user_query:
        return jsonify({"error": "Missing message"}), 400
    
    chat_memory.append({"role": "user", "content": user_query})
    
    while True: 
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=chat_memory
        )

        parsed_output = json.loads(response.choices[0].message.content)
        chat_memory.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get('content')}")
            continue

        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if available_tools.get(tool_name, False) != False: 
                tool_fn = available_tools[tool_name]["fn"]
                if isinstance(tool_input, dict):
                    output = tool_fn(**tool_input)
                else:
                    output = tool_fn(tool_input)
                chat_memory.append({ "role": "assistant", "content": json.dumps({"step": "observe", "output": output}) })
                continue

        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get('content')}")
            return jsonify({"message": parsed_output.get("content")})

if __name__ == "__main__":
    app.run(debug=True)