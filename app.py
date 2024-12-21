from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

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
    
    response = requests.post(OLLAMA_API_URL_SUM, json=payload, headers=headers)
    data = response.json()
    
    if 'message' in data:
        print(data)
        return data['message']['content']
    else:
        return "Error: 'message' key not found in Ollama's response."

def query_ollama(messages):
    
    payload = {
        'messages': messages,
        'model': 'BOLT5',
        'stream': False
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
    data = response.json()
    
    if 'message' in data:
        return data['message']['content']
    else:
        return "Error: 'message' key not found in Ollama's response."

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/api/generate', methods=['POST'])
def generate():

    user_prompt = request.json.get('prompt')

    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    #if len(conversation_history) >= 5:
        
        conversation_history.append({"role": "user", "content": "Summarize this conversation history in a few sentences. Keep important details no matter how long the summary gets but do your best to paraphrase."})
        
        # Get the summary and clear the history
        chat_summary = query_ollama_sum(conversation_history)
        conversation_history.clear()
        conversation_history.append({"role": "assistant", "content": chat_summary})

    
    conversation_history.append({"role": "user", "content": user_prompt})

    
    response_text = query_ollama(conversation_history)

    
    conversation_history.append({"role": "assistant", "content": response_text})

    
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
