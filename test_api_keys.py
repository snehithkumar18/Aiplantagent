import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    print("\n--- Testing GROQ API ---")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY is missing in .env")
        return
    
    # Mask key for privacy
    masked = api_key[:4] + "*" * (len(api_key)-8) + api_key[-4:] if len(api_key) > 8 else "***"
    print(f"Key found: {masked}")

    url = "https://api.groq.ai/openai/v1/chat/completions"  # Standard OpenAI-compatible endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [{"role": "user", "content": "Hello, are you working?"}],
        "model": "llama-3.3-70b-versatile", 
        "max_tokens": 10
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ GROQ API Success!")
            print(f"Response: {r.json()['choices'][0]['message']['content']}")
        else:
            print(f"❌ GROQ API Failed: {r.status_code}")
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"❌ GROQ Connection Error: {e}")

def test_hf():
    print("\n--- Testing Hugging Face API ---")
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY is missing")
        return
    
    headers = {"Authorization": f"Bearer {api_key}"}
    # Test with a simple model
    url = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # 200 or 503 (loading) usually means auth is good
        if r.status_code in [200, 503]:
             print(f"✅ HF API Auth seems OK (Status: {r.status_code})")
        elif r.status_code == 401:
             print("❌ HF API Unauthorized (Invalid Key)")
        else:
             print(f"⚠️ HF API Status: {r.status_code} - {r.text[:100]}")
    except Exception as e:
         print(f"❌ HF Connection Error: {e}")

def test_weather():
     print("\n--- Testing OpenWeather API ---")
     api_key = os.getenv("OPENWEATHER_API_KEY")
     if not api_key:
         print("❌ OPENWEATHER_API_KEY is missing")
         return
         
     url = f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
     try:
         r = requests.get(url, timeout=10)
         if r.status_code == 200:
             print("✅ OpenWeather API Success!")
         elif r.status_code == 401:
             print("❌ OpenWeather API Unauthorized (Invalid Key)")
         else:
             print(f"❌ OpenWeather Failed: {r.status_code}")
     except Exception as e:
         print(f"❌ Weather Connection Error: {e}")

if __name__ == "__main__":
    # test_groq()
    test_hf()
    # test_weather()
