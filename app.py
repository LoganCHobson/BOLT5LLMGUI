from flask import Flask, request, jsonify, render_template
import requests
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  

OLLAMA_API_URL = 'http://localhost:11434/api/chat'  
OLLAMA_API_URL_SUM = 'http://localhost:11434/api/generate'

conversation_history = []

def query_ollama_sum(messages):
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
            print(data)
            return data['message']['content']
        else:
            return "Error: 'message' key not found in Ollama's response."
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

def query_ollama(messages):
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
        return jsonify({'error': str(e)}), 500

def summarize_conversation():
    """Summarize conversation if it exceeds 5 messages."""
    if len(conversation_history) >= 5:
        conversation_history.append({
            "role": "user", 
            "content": "Summarize this conversation history in a few sentences. Keep important details no matter how long the summary gets but do your best to paraphrase."
        })
        chat_summary = query_ollama_sum(conversation_history)
        conversation_history.clear() 
        conversation_history.append({"role": "assistant", "content": chat_summary})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    user_prompt = request.json.get('prompt')

    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    
    summarize_conversation()

    conversation_history.append({"role": "user", "content": user_prompt})
    
    response_text = query_ollama(conversation_history)

    conversation_history.append({"role": "assistant", "content": response_text})

    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
