import os
import requests
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# Config
HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "Daksh159/plant-disease-mobilenetv2")

# Test Image (use one found in uploads)
TEST_IMAGE = "uploads/Tomato-late-blight-72605cba08f2483aae0fd8f1dc3532a9.jpg"

if not os.path.exists(TEST_IMAGE):
    print(f"❌ Test image not found at {TEST_IMAGE}", flush=True)
    # Try to find another one
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                TEST_IMAGE = os.path.join(root, file)
                break
        if os.path.exists(TEST_IMAGE): break

if not os.path.exists(TEST_IMAGE):
    print("❌ No images found in uploads/ to test with.", flush=True)
    exit(1)

def test_hf_model():
    print(f"\n--- Testing Hugging Face Model: {HF_MODEL} ---", flush=True)
    if not HF_KEY:
        print("❌ HUGGINGFACE_API_KEY missing", flush=True)
        return

    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_KEY}"}

    print(f"Sending request to {api_url}...", flush=True)

    try:
        with open(TEST_IMAGE, "rb") as f:
            data = f.read()
        
        response = requests.post(api_url, headers=headers, data=data, timeout=30)
        print(f"Status Code: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ HF Response JSON:", flush=True)
                print(json.dumps(result, indent=2), flush=True)
            except:
                print(f"⚠️ HF Response Text (Not JSON): {response.text}", flush=True)
        else:
            print(f"❌ HF Failed: {response.text}", flush=True)

    except Exception as e:
        print(f"❌ HF Exception: {e}", flush=True)

if __name__ == "__main__":
    test_hf_model()
