from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from collections import defaultdict, deque

app = Flask(__name__)
CORS(app)

OLLAMA_API_URL = 'http://localhost:11434/api/chat'  


chat_histories = defaultdict(lambda: deque(maxlen=10))  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    user_id = data.get('user_id', 'default')  

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    
    user_history = chat_histories[user_id]
    user_history.append({'role': 'user', 'content': prompt})  

    
    response = query_llama(list(user_history))

    if 'error' in response:
        return jsonify({'error': response['error']}), 500

 
    user_history.append({'role': 'assistant', 'content': response['response']})

    return jsonify({'response': response['response']})

def query_llama(context):
    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        'model': 'BOLT5',
        'messages': context
    }

    try:
        api_response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, stream=True)

        if api_response.status_code != 200:
            return {'error': f'API returned status code {api_response.status_code}'}

        full_response = ''
        for chunk in api_response.iter_content(chunk_size=1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                try:
                    json_chunk = json.loads(decoded_chunk)
                    part = json_chunk["message"]["content"]
                    full_response += part
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {decoded_chunk}")

        if not full_response.strip():
            return {'error': 'Empty response from the model'}

        return {'response': full_response.strip()}

    except Exception as e:
        return {'error': f'Error querying Ollama API: {str(e)}'}

@app.route('/api/reset', methods=['POST'])
def reset_context():
    data = request.get_json()
    user_id = data.get('user_id', 'default')  

    if user_id in chat_histories:
        chat_histories.pop(user_id)  
    return jsonify({'message': 'Chat history reset successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
