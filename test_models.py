import os, requests, json
key = os.getenv('GROQ_API_KEY')
r = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {key}'})
models = [m['id'] for m in r.json().get('data', [])]
with open('models_output.txt', 'w') as f:
    f.write(", ".join(models))
print("Done")
