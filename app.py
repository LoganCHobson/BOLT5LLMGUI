import requests
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

OLLAMA_API_URL = 'http://localhost:11434/api/chat'  


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')  
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400  

    print("Received prompt:", prompt)  
    
   
    response = query_llama(prompt)  

    print("Response from Ollama API:", response)  
    
    if 'error' in response:
        return jsonify({'error': response['error']}), 500  

    return jsonify({'response': response['response']})  

def query_llama(prompt):
    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        'model': 'BOLT5',
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        
        api_response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, stream=True)
        
        print("Ollama API Response Status:", api_response.status_code)  
        
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

if __name__ == '__main__':
    app.run(debug=True)

