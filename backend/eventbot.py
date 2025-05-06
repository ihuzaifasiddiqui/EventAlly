from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
import os
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Store the current question index in memory
current_question_index = 0

# Form configuration
form_config = {
    'formUrl': 'https://docs.google.com/forms/d/e/1FAIpQLSefrkNNYydNTp-hQwBapGP1lg1uZP8G2ghSE5GSeaNere06Tw/viewform',
    'fields': [
        {
      "entryId": "entry.1274867366",
      "question": "What is your name?"
    },
    {
      "entryId": "entry.1546935728",
      "question": "how was your experience?"
    },
    {
      "entryId": "entry.1774645751",
      "question": "How would you rate it on a scale of 1 to 5?"
    }
    ]
}

@app.route("/")
def hello_world():
    return jsonify({'message': "Hello from BE", 'count': 10})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        global current_question_index
        data = request.get_json()
        user_response = data.get('prompt')

        # If no response provided, return the current question
        if not user_response:
            if current_question_index < len(form_config['fields']):
                return jsonify({
                    'message': form_config['fields'][current_question_index]['question'],
                    'done': False
                })
            else:
                return jsonify({
                    'message': '✅ Thank you! Your feedback has been submitted successfully.',
                    'done': True
                })

        # Save the response
        if current_question_index < len(form_config['fields']):
            entry_id = form_config['fields'][current_question_index]['entryId']
            form_data = {entry_id: user_response}
            
            # Submit to Google Form
            form_post_url = form_config['formUrl'].replace('/viewform', '/formResponse')
            res = requests.post(form_post_url, data=form_data)
            
            current_question_index += 1

            # If there are more questions, return the next one
            if current_question_index < len(form_config['fields']):
                return jsonify({
                    'message': form_config['fields'][current_question_index]['question'],
                    'done': False
                })
            else:
                return jsonify({
                    'message': '✅ Thank you! Your feedback has been submitted successfully.',
                    'done': True
                })
        else:
            return jsonify({
                'message': '❌ No more questions to answer.',
                'done': True
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
