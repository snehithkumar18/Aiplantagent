import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

print(f"GROQ_API_KEY starts with: {str(GROQ_API_KEY)[:5] if GROQ_API_KEY else 'None'}")

if not GROQ_API_KEY:
    print("No GROQ_API_KEY")
    exit(1)

# try a simple request to vision model
# create a tiny valid dummy image (1x1 red pixel)
dummy_img = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
b64 = base64.b64encode(dummy_img).decode('utf-8')

payload = {
    "model": "llama-3.2-90b-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is this?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 10
}

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(response.text)
except Exception as e:
    print(e)

