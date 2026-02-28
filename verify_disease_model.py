import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

# Config
HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "Daksh159/plant-disease-mobilenetv2")
GROQ_MODEL = "llama-3.2-90b-vision-preview"

# Test Image (use one found in uploads)
TEST_IMAGE = "uploads/Tomato-late-blight-72605cba08f2483aae0fd8f1dc3532a9.jpg"

if not os.path.exists(TEST_IMAGE):
    print(f"❌ Test image not found at {TEST_IMAGE}")
    # Try to find another one
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                TEST_IMAGE = os.path.join(root, file)
                print(f"✅ Found alternative image: {TEST_IMAGE}")
                break
        if os.path.exists(TEST_IMAGE): break

if not os.path.exists(TEST_IMAGE):
    print("❌ No images found in uploads/ to test with.")
    exit(1)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_hf_model():
    print(f"\n--- Testing Hugging Face Model: {HF_MODEL} ---")
    if not HF_KEY:
        print("❌ HUGGINGFACE_API_KEY missing")
        return

    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_KEY}"}

    try:
        with open(TEST_IMAGE, "rb") as f:
            data = f.read()
        
        response = requests.post(api_url, headers=headers, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ HF Response JSON:")
                print(json.dumps(result, indent=2))
            except:
                print(f"⚠️ HF Response Text (Not JSON): {response.text}")
        else:
            print(f"❌ HF Failed: {response.text}")

    except Exception as e:
        print(f"❌ HF Exception: {e}")

def test_groq_vision():
    print(f"\n--- Testing Groq Vision Model: {GROQ_MODEL} ---")
    if not GROQ_KEY:
        print("❌ GROQ_API_KEY missing")
        return

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    base64_img = encode_image(TEST_IMAGE)
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Identify this plant disease. Return JSON with 'disease' key."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print("✅ Groq Vision Content:")
                print(content)
            except:
                print(f"⚠️ Groq Response JSON: {response.json()}")
        else:
            print(f"❌ Groq Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Groq Exception: {e}")

def check_internet():
    print("\n--- Checking Internet Connection ---")
    try:
        import socket
        ip = socket.gethostbyname("google.com")
        print(f"✅ Google.com resolved to {ip}")
        ip_hf = socket.gethostbyname("api-inference.huggingface.co")
        print(f"✅ Hugging Face resolved to {ip_hf}")
        ip_groq = socket.gethostbyname("api.groq.ai")
        print(f"✅ Groq resolved to {ip_groq}")
    except Exception as e:
        print(f"❌ DNS Resolution Failed: {e}")

if __name__ == "__main__":
    check_internet()
    print(f"Testing with image: {TEST_IMAGE}")
    test_hf_model()
    test_groq_vision()
