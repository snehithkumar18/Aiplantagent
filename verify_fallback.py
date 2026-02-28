import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = "Salesforce/blip-image-captioning-large"
TEST_IMAGE = "uploads/Tomato-late-blight-72605cba08f2483aae0fd8f1dc3532a9.jpg"

if not os.path.exists(TEST_IMAGE):
    # finding image... default to whatever
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                TEST_IMAGE = os.path.join(root, file)
                break
        if os.path.exists(TEST_IMAGE): break

def test_caption():
    print(f"Testing Caption Model: {HF_MODEL}")
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_KEY}"}

    try:
        with open(TEST_IMAGE, "rb") as f:
            data = f.read()
            
        print("Sending request...")
        response = requests.post(api_url, headers=headers, data=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Error:", response.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_caption()
