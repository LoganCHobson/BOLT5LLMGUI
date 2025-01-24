import os
import json
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_API_URL = 'http://localhost:11434/api/chat'
OLLAMA_API_URL_SUM = 'http://localhost:11434/api/generate'

CONVERSATION_DIR = 'conversations'

if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

conversation_history = {}

def query_ollama_sum(messages):
    """Query Ollama to summarize the conversation"""
    payload = {
        'messages': messages,
        'model': 'BOLT5',
        'stream': False
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(OLLAMA_API_URL_SUM, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'message' in data:
            return data['message']['content']
        else:
            return "Error: 'message' key not found in Ollama's response."
    except requests.exceptions.RequestException as e:
        return str(e)

def query_ollama(messages):
    """Query Ollama to generate a response based on conversation history"""
    payload = {
        'messages': messages,
        'model': 'BOLT5',
        'stream': False
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'message' in data:
            return data['message']['content']
        else:
            return "Error: 'message' key not found in Ollama's response."
    except requests.exceptions.RequestException as e:
        return str(e)

def save_conversation_to_file(conversation_id, conversation_history):
    """Save conversation history to a JSON file"""
    with open(os.path.join(CONVERSATION_DIR, f"{conversation_id}.json"), 'w') as f:
        json.dump(conversation_history, f)

def load_conversation_from_file(conversation_id):
    """Load conversation history from a JSON file"""
    try:
        with open(os.path.join(CONVERSATION_DIR, f"{conversation_id}.json"), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get the list of all conversation files"""
    conversations = [f.replace('.json', '') for f in os.listdir(CONVERSATION_DIR) if f.endswith('.json')]
    return jsonify({'conversations': conversations})

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get the conversation history for a given conversation"""
    conversation_history = load_conversation_from_file(conversation_id)
    return jsonify({'conversation': conversation_history})

@app.route('/api/generate', methods=['POST'])
def generate():
    """Handle the prompt and generate a response"""
    user_prompt = request.json.get('prompt')
    conversation_id = request.json.get('conversation_id', 'new_conversation')

    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    conversation_history = load_conversation_from_file(conversation_id) if conversation_id != 'new_conversation' else []

    conversation_history.append({"role": "user", "content": user_prompt})

    if len(conversation_history) >= 5:
        summary = query_ollama_sum(conversation_history)
        conversation_history.append({"role": "assistant", "content": summary})

    response_text = query_ollama(conversation_history)

    conversation_history.append({"role": "assistant", "content": response_text})

    save_conversation_to_file(conversation_id, conversation_history)

    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
