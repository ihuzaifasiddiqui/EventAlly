from dotenv import load_dotenv
import json
from openai import OpenAI
import requests
import os

load_dotenv()

client = OpenAI( api_key=os.environ.get("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/" )

# Form configuration (we'll still use these IDs for submission)
form_config = {
    'formUrl': 'https://docs.google.com/forms/d/e/1FAIpQLSefrkNNYydNTp-hQwBapGP1lg1uZP8G2ghSE5GSeaNere06Tw/viewform',
    'fields': [
        {
            "entryId": "entry.1274867366",
            "purpose": "Get the user's name for personalization"
        },
        {
            "entryId": "entry.1546935728",
            "purpose": "Understand their overall experience"
        },
        {
            "entryId": "entry.1774645751",
            "purpose": "Get a numerical rating of their experience"
        }
    ]
}

# Feedback state management
feedback_state = {
    'active': False,
    'current_index': 0,
    'responses': {}
}

def submit_to_google_forms(form_data):
    """Submit responses to Google Forms"""
    form_post_url = form_config['formUrl'].replace('/viewform', '/formResponse')
    try:
        res = requests.post(form_post_url, data=form_data)
        return res.status_code == 200
    except Exception as e:
        print(f"Error submitting to Google Forms: {e}")
        return False

def generate_conversational_question(field_info, previous_responses=None):
    """Generate natural language questions based on the field purpose"""
    purpose = field_info['purpose']
    
    if "name" in purpose.lower():
        return (
            "Before we begin, may I know what I should call you? "
            "First name is perfectly fine!"
        )
    elif "overall experience" in purpose.lower():
        name = previous_responses.get('entry.1274867366', 'there')
        return (
            f"So {name}, I'd love to hear about your experience in your own words. "
            "How did everything go for you today?"
        )
    elif "numerical rating" in purpose.lower():
        return (
            "On a scale from 1 to 5, where 1 means 'needs improvement' and "
            "5 means 'excellent', how would you rate your experience overall?"
        )
    else:
        return f"Could you tell me about {purpose.lower()}?"

def handle_feedback_interaction(user_input=None):
    """Manage the conversational feedback flow"""
    global feedback_state
    
    # Start feedback collection if not active
    if not feedback_state['active']:
        feedback_state = {
            'active': True,
            'current_index': 0,
            'responses': {}
        }
        current_field = form_config['fields'][0]
        return generate_conversational_question(current_field)
    
    # Store the response if provided
    if user_input:
        current_field = form_config['fields'][feedback_state['current_index']]
        feedback_state['responses'][current_field['entryId']] = user_input
        feedback_state['current_index'] += 1
    
    # Check if we have more questions
    if feedback_state['current_index'] < len(form_config['fields']):
        current_field = form_config['fields'][feedback_state['current_index']]
        return generate_conversational_question(
            current_field,
            feedback_state['responses']
        )
    
    # Submit all responses when done
    success = submit_to_google_forms(feedback_state['responses'])
    feedback_state['active'] = False
    
    name = feedback_state['responses'].get('entry.1274867366', '')
    if success:
        return (
            f"✅ Thank you {name}! Your feedback means a lot to us. "
            "We'll use it to make our service even better."
        )
    else:
        return (
            f"❌ Oh no {name}, we hit a small snag saving your feedback. "
            "The team will still hear about your thoughts though!"
        )

# System prompt for the AI
system_prompt = """
You are FeedbackBot, a friendly AI assistant whose sole purpose is to collect user feedback through natural conversation.

Guidelines:
1. Be warm, empathetic, and human-like in all interactions
2. Adapt your questions based on previous responses (e.g., use the user's name)
3. Keep questions conversational but ensure you collect all required information
4. If users go off-topic, gently guide them back to the feedback process
5. Show appreciation for their time and input

Tone:
- Friendly but professional
- Casual but not overly familiar
- Positive and encouraging

Response structure:
- Always respond in complete sentences
- Use natural language, not robotic Q&A
- Add occasional pleasantries to keep it human
"""

def generate_chat_response(messages):
    """Generate AI response using the conversation history"""
    response = client.chat.completions.create(
        model="gemini-1.5-pro",
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "assistant", "content": "Hi there! 👋 We're always looking to improve, and your thoughts would be incredibly helpful. Mind sharing some quick feedback?"}
]

print("🤖: Hi there! 👋 We're always looking to improve, and your thoughts would be incredibly helpful. Mind sharing some quick feedback?")

while True:
    user_input = input("> ")
    
    # Handle exit commands
    if user_input.lower() in ['exit', 'quit', 'bye', 'no', 'not now']:
        if feedback_state['active']:
            print("🤖: No problem at all! Thanks for considering it. Have a great day!")
        else:
            print("🤖: Thanks for stopping by! Come back anytime.")
        break
    
    # Add user message to conversation history
    messages.append({"role": "user", "content": user_input})
    
    # Process the feedback interaction
    if feedback_state['active']:
        # Get the next feedback question
        bot_response = handle_feedback_interaction(user_input)
        
        # Check if feedback is complete
        if not feedback_state['active']:
            print(f"🤖: {bot_response}")
            break
    else:
        # Start feedback collection with a generated response
        bot_response = generate_chat_response(messages)
        if "feedback" in bot_response.lower() or "thoughts" in bot_response.lower():
            feedback_state = {
                'active': True,
                'current_index': 0,
                'responses': {}
            }
    
    # Generate conversational response
    if feedback_state['active']:
        current_field = form_config['fields'][feedback_state['current_index']]
        question_purpose = current_field['purpose']
        
        # Create context for the AI to generate a follow-up
        context_messages = messages.copy()
        context_messages.append({
            "role": "system",
            "content": f"Current feedback goal: {question_purpose}. Respond naturally to continue the conversation."
        })
        
        bot_response = generate_chat_response(context_messages)
    
    print(f"🤖: {bot_response}")
    messages.append({"role": "assistant", "content": bot_response})