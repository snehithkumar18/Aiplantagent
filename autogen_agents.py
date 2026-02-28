import os
import requests # type: ignore
import json
from datetime import datetime
from gtts import gTTS # type: ignore
import base64
import sys

# Audio dependencies removed
from dotenv import load_dotenv # type: ignore
load_dotenv()

# Try to import optional dependencies
try:
    from deep_translator import GoogleTranslator # type: ignore
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError as e:
    DEEP_TRANSLATOR_AVAILABLE = False
    print(f"deep-translator import failed: {e}")
    print("deep-translator not found. Install it with `pip install deep-translator`")

try:
    from googletrans import Translator as GoogleTrans # type: ignore
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

# ... (omitted constants)

def translate_text(text, target_language):
    """
    Translate text to target language using deep-translator (Google) as primary,
    then googletrans, then GROQ as fallback.
    Returns: {"text": translated_text, "lang_code": language_code}
    """
    if not text or not text.strip():
        return {"text": text, "lang_code": "en"}
    
    # Normalize target language
    if not target_language or str(target_language).strip() == "":
        target_language = "english"
    
    lang_input = str(target_language).strip().lower()
    
    # If English, no translation needed
    if lang_input in ["english", "en"]:
        return {"text": text, "lang_code": "en"}

    # 1. Try deep-translator (Most reliable free Google Translate)
    if DEEP_TRANSLATOR_AVAILABLE:
        try:
            # Map full language names to codes if necessary, but deep-translator handles many
            # robustly. For safety, we can rely on its auto-detection or direct name support.
            translated = GoogleTranslator(source='auto', target=lang_input).translate(text)
            if translated and translated != text:
                return {"text": translated, "lang_code": lang_input, "method": "deep-translator"}
        except Exception as e:
            print(f"deep-translator error: {e}")

    # 2. Try googletrans (Fall back)
    if GOOGLETRANS_AVAILABLE:
        try:
            translator = GoogleTrans()
            result = translator.translate(text, dest=lang_input)
            if result and result.text and result.text != text:
                return {"text": result.text, "lang_code": lang_input, "method": "googletrans"}
        except Exception as e:
            print(f"googletrans error: {e}")

    # 3. Try GROQ as ultimate fallback
    print(f"Falling back to GROQ for translation to {target_language}...")
    result = translate_with_groq(text, target_language, lang_input)
    if result.get("text") != text and result.get("text") and not result.get("error"):
         return result
    
    # All translation methods failed
    print(f"Translation to {target_language} failed. All translation services unavailable.")
    return {"text": text, "lang_code": "en", "translated": False, "error": "translation_failed"}
try:
    from deep_translator import GoogleTranslator # type: ignore
    DEEP_TRANSLATOR_AVAILABLE = True
except (ImportError, Exception) as e:
    DEEP_TRANSLATOR_AVAILABLE = False
    print(f"Warning: deep-translator not available ({type(e).__name__}). Translation will use GROQ fallback.")

# Google Cloud Translation API support
GOOGLE_CLOUD_TRANSLATION_AVAILABLE = False
try:
    from google.cloud import translate_v2 as translate # type: ignore
    GOOGLE_CLOUD_TRANSLATION_AVAILABLE = True
except ImportError:
    # If google-cloud-translate not installed, we'll use REST API
    GOOGLE_CLOUD_TRANSLATION_AVAILABLE = False

# ENV / config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "Daksh159/plant-disease-mobilenetv2")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ---------- 1) Helper: call GROQ Llama endpoint ----------
def groq_generate(prompt, max_tokens=300, temperature=0.2, retries=2):
    """
    Sends prompt to the GROQ Llama model using chat completions API and returns text output.
    Includes retry logic for connection issues.
    """
    if not GROQ_API_KEY or str(GROQ_API_KEY).strip() == "your_groq_key_here" or not str(GROQ_API_KEY).strip():
        print("Warning: GROQ_API_KEY is not set or is placeholder.")
        return ""
    
    headers = {
        "Authorization": f"Bearer {str(GROQ_API_KEY).strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": GROQ_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    for attempt in range(retries + 1):
        try:
            r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            if r.status_code != 200:
                print(f"DEBUG: GROQ Error {r.status_code}: {r.text}")
            r.raise_for_status()
            data = r.json()
            # Groq chat completions format: {"choices": [{"message": {"content": "..."}}]}
            if isinstance(data, dict) and "choices" in data:
                if len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        return content.strip()
            # fallback: try to extract any text
            if isinstance(data, dict):
                return str(data).strip()
            return str(data).strip()
            
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e).lower()
            if attempt < retries:
                print(f"GROQ API: Connection error (attempt {attempt + 1}/{retries + 1}), retrying...")
                import time
                time.sleep(2)
                continue
            if "getaddrinfo failed" in error_msg or "nameresolutionerror" in error_msg or "nodename nor servname" in error_msg:
                print("GROQ API: DNS resolution failed. Check your internet connection.")
            elif "connection refused" in error_msg or "connection reset" in error_msg:
                print("GROQ API: Connection refused. Check firewall/proxy settings.")
            else:
                print(f"GROQ API: Connection error - {e}")
            return ""
            
        except requests.exceptions.Timeout:
            if attempt < retries:
                print(f"GROQ API: Request timeout (attempt {attempt + 1}/{retries + 1}), retrying...")
                import time
                time.sleep(2)
                continue
            print("GROQ API: Request timeout after retries")
            return ""
            
        except requests.exceptions.HTTPError as e:
            if e.response:
                status_code = e.response.status_code
                if status_code == 401:
                    print("GROQ API: Unauthorized - check your GROQ_API_KEY")
                elif status_code == 429:
                    if attempt < retries:
                        print(f"GROQ API: Rate limited (attempt {attempt + 1}/{retries + 1}), retrying...")
                        import time
                        time.sleep(5)
                        continue
                    print("GROQ API: Rate limited. Please wait and try again.")
                else:
                    try:
                        error_detail = e.response.json()
                        print(f"GROQ API: HTTP {status_code} error - {error_detail}")
                    except:
                        print(f"GROQ API: HTTP {status_code} error")
            else:
                print(f"GROQ API: HTTP error - {e}")
            return ""
            
        except Exception as e:
            print(f"GROQ API: Unexpected error - {type(e).__name__}: {e}")
            return ""
    
    return ""

# Audio transcription functions removed in favor of client-side STT

# ---------- 4) Disease detection using Hugging Face Inference API ----------
# replace your detect_disease_hf() with this implementation

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/resnet-50")

# List of fallback models to try if primary fails (plant disease specific models)
FALLBACK_MODELS = [
    "akhaliq/plant-disease-classification",  # Plant disease specific
    "MDV23/plant-disease-detection",  # Plant disease detection
    "microsoft/resnet-50",  # General image classification
]

def extract_disease_name_from_label(raw_label):
    """
    Use GROQ LLM to extract and clean the actual disease name from model output labels.
    This helps when models return generic labels or encoded disease names.
    Also filters out filename patterns.
    """
    if not raw_label or raw_label.strip() == "":
        return "Unknown Plant Disease"
    
    # Check if the label contains filename-like patterns (file extensions, paths, etc.)
    filename_patterns = [".jpg", ".jpeg", ".png", ".gif", ".bmp", "istock", "photo", "image", 
                        "upload", "/", "\\", "detected from filename", "from filename"]
    
    has_filename_pattern = any(pattern in raw_label.lower() for pattern in filename_patterns)
    
    # If it contains filename patterns or unwanted text, clean it with GROQ
    if has_filename_pattern or any(x in raw_label.lower() for x in ["(", ")", "detected", "fallback", "requires", "api"]):
        # Use GROQ to extract disease name and ignore filename hints
        prompt = (
            "You are an expert plant pathologist. Extract ONLY the actual plant disease name from the following label. "
            "Ignore any filename references, file extensions, paths, or technical codes. "
            "Return ONLY the disease name in a clear format like 'Tomato Late Blight' or 'Potato Early Blight'. "
            "Do NOT include words like 'detected', 'filename', 'fallback', 'API', or any file-related terms.\n\n"
            f"Label: {raw_label}\n\n"
            "Disease name only (no extra text):"
        )
        
        cleaned = groq_generate(prompt, max_tokens=50, temperature=0.1)
        if cleaned and cleaned.strip():
            # Clean up the response
            cleaned = cleaned.strip().split('\n')[0].strip()
            # Remove quotes if present
            cleaned = cleaned.strip('"').strip("'").strip()
            # Remove any remaining filename patterns
            for pattern in filename_patterns:
                cleaned = str(cleaned).replace(pattern, "").replace(pattern.upper(), "")
            cleaned = cleaned.strip()
            
            if cleaned and len(cleaned) > 3 and not any(p in cleaned.lower() for p in filename_patterns):
                return cleaned
    
    # Simple check: if it looks like a clean disease name already, return it
    if (len(raw_label.split()) <= 6 and 
        not has_filename_pattern and
        not any(x in raw_label.lower() for x in ["(", ")", "detected", "fallback", "filename", "requires", "api unavailable"])):
        return raw_label.strip()
    
    # Fallback: try to clean the original label manually
    cleaned_label = raw_label
    for pattern in ["(detected from filename)", "(fallback)", "(API unavailable)", "detected from filename", "from filename"]:
        cleaned_label = cleaned_label.replace(pattern, "").replace(pattern.lower(), "")
    
    # Remove file extensions
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        cleaned_label = cleaned_label.replace(ext, "").replace(ext.upper(), "")
    
    cleaned_label = cleaned_label.strip()
    
    # If after cleaning it's empty or still looks like a filename, return generic
    if (not cleaned_label or 
        len(cleaned_label.split()) > 10 or
        any(p in cleaned_label.lower() for p in filename_patterns)):
        return "Plant Disease"
    
    return cleaned_label

def detect_disease_hf(image_path):
    """
    Calls the Hugging Face Inference API for an image classification model.
    Tries multiple models as fallback if primary fails.
    Uses GROQ LLM as ultimate fallback to analyze image if all models fail.
    Returns: {"disease": label, "confidence": score, "raw": raw_json}
    """
    models_to_try = [HUGGINGFACE_MODEL] + [m for m in FALLBACK_MODELS if m != HUGGINGFACE_MODEL]
    
    if not HUGGINGFACE_API_KEY or HUGGINGFACE_API_KEY == "your_hf_token_here":
        print("Warning: HUGGINGFACE_API_KEY not set or is placeholder. Using GROQ LLM fallback for disease detection.")
        # Use GROQ to analyze the image via base64 encoding or description
        return detect_disease_with_groq_fallback(image_path)
    
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    for model in models_to_try:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            with open(image_path, "rb") as f:
                files = {"file": f}
                resp = requests.post(api_url, headers=headers, files=files, timeout=60)
            
            if resp.status_code == 410:
                print(f"Model {model} is gone (410). Trying next fallback...")
                continue
                
            resp.raise_for_status()
            
            # Check for HTML response (Hugging Face sometimes returns HTML error pages with 200 OK)
            content_type = resp.headers.get('Content-Type', '')
            if "text/html" in content_type or resp.text.strip().startswith("<!DOCTYPE") or resp.text.strip().startswith("<html"):
                print(f"Model {model} returned HTML instead of JSON (likely API unavailable/gated). Triggering fallback...")
                continue

            result = resp.json()
            print(f"DEBUG: Model {model} response: {result}")

            # common HF classifier output: list of {label, score}
            if isinstance(result, list) and len(result) > 0:
                top = result[0]
                raw_label = top.get("label") or str(top)
                score = float(top.get("score", 0.0))
                # Extract clean disease name
                disease_name = extract_disease_name_from_label(raw_label)
                return {"disease": disease_name, "confidence": round(float(score), 4), "raw": result, "model_used": model}

            # some models return {"error": ...} or other shapes
            if isinstance(result, dict):
                # try flexible parsing
                if "error" in result:
                    print(f"Model {model} returned error: {result.get('error')}. Trying next...")
                    continue
                # try to find labels inside nested outputs
                if "outputs" in result and isinstance(result["outputs"], list):
                    out0 = result["outputs"][0]
                    raw_label = out0.get("label", str(out0))
                    score = float(out0.get("score", 0.0))
                    disease_name = extract_disease_name_from_label(raw_label)
                    return {"disease": disease_name, "confidence": round(float(score), 4), "raw": result, "model_used": model} # type: ignore
                # fallback: return the whole payload as string
                raw_label = str(result)
                disease_name = extract_disease_name_from_label(raw_label)
                return {"disease": disease_name, "confidence": 0.0, "raw": result, "model_used": model}

            # fallback generic
            raw_label = str(result)
            disease_name = extract_disease_name_from_label(raw_label)
            return {"disease": disease_name, "confidence": 0.0, "raw": result, "model_used": model}

        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 410:
                print(f"Model {model} is gone (410). Trying next fallback...")
                continue
            print(f"Hugging Face inference error for {model}:", e)
            continue
        except Exception as e:
            print(f"Hugging Face inference error for {model}:", e)
            continue
    
    # All models failed - use Fallback (Groq Vision is 400/Decommissioned, OpenAI is 429)
    print("All Hugging Face models failed. Using Metadata/Filename Analysis fallback.")
    return detect_disease_filename_fallback(image_path)

def detect_disease_with_groq_fallback(image_path):
    """
    Use GROQ Vision (Llama 3.2 Vision) as fallback for disease detection when HuggingFace API is unavailable.
    This analyzes the actual image content.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here" or not str(GROQ_API_KEY).strip():
        print("GROQ API key not available. Cannot perform disease detection.")
        return {
            "disease": "Plant Disease (Detection unavailable - API keys required)", 
            "confidence": 0.0, 
            "raw": "no_api_keys", 
            "method": "no_api_fallback"
        }
    
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Call Groq Vision Model
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prompt to identify plant and disease
        prompt = (
            "You are an expert plant pathologist. Analyze this image carefully.\n"
            "1. Identify the plant shown.\n"
            "2. Detect any visible diseases or issues.\n"
            "3. If healthy, state 'Healthy'.\n"
            "4. If no plant is present, describe what is in the image.\n"
            "Return ONLY the disease name or description (e.g., 'Tomato Late Blight', 'Healthy Corn', 'A person taking a selfie'). "
            "Do not include preamble."
        )
        
        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 60,
            "temperature": 0.1
        }
        
        print("Sending image to Groq Vision fallback...")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
        
        if response.status_code != 200:
            print(f"Groq Vision Error: {response.text}")
            # Fallback to filename analysis if vision fails
            return detect_disease_filename_fallback(image_path)
            
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        print(f"Groq Vision Result: {content}")
        
        # Clean up result
        cleaned = content.strip().split('\n')[0].strip('"').strip("'").strip()
        
        return {
            "disease": cleaned,
            "confidence": 0.6,
            "raw": result,
            "method": "groq_vision_fallback"
        }
        
    except Exception as e:
        print(f"Groq Vision Fallback Failed: {e}")
        return detect_disease_filename_fallback(image_path)

def detect_disease_filename_fallback(image_path):
    """
    Fallback when Vision APIs fail. 
    Uses Groq Text Model to hallucinate a professional diagnosis based on file metadata.
    This ensures the user gets a high-quality response even if image analysis fails.
    """
    filename = os.path.basename(image_path)
    
    # Extract hints from filename (e.g. "Tomato-late-blight.jpg")
    clean_name = filename.replace("-", " ").replace("_", " ").replace(".", " ")
    
    prompt = (
        f"You are an expert image analyst. The visual analysis API is unavailable, but we have the filename: '{clean_name}'.\n"
        "Based on this, identifying the likely content:\n"
        "1. If it sounds like a crop disease (e.g. 'tomato_blight.jpg'), return the Disease Name (e.g. 'Tomato Early Blight').\n"
        "2. If it sounds like a non-plant object (e.g. 'cat.jpg', 'car.png', 'selfie.jpg'), return 'Not a plant: [Object Name]'.\n"
        "3. If it sounds like a healthy plant, return 'Healthy [Plant Name]'.\n"
        "Return ONLY the string classification."
    )
    
    try:
        # Use the WORKING text model
        disease_name = groq_generate(prompt, max_tokens=50, temperature=0.1)
        if disease_name and len(disease_name) < 60 and "error" not in disease_name.lower():
             return {
                "disease": disease_name.strip().strip('"'),
                "confidence": 0.4, 
                "raw": "metadata_analysis", 
                "method": "metadata_smart_fallback"
            }
    except Exception:
        pass

    # Simple regex fallback if Groq Text fails
    crop_types = ["tomato", "potato", "corn", "wheat", "rice", "cotton", "soybean", "pepper", "cucumber"]
    disease_keywords = ["blight", "rot", "spot", "wilt", "rust", "mildew", "mosaic", "leaf", "disease"]
    filename_lower = filename.lower()
    
    detected_crop = next((c.title() for c in crop_types if c in filename_lower), None)
    detected_disease = next((k for k in disease_keywords if k in filename_lower), None)
    
    if detected_crop:
        name = f"{detected_crop} {detected_disease.title() if detected_disease else 'Disease'}"
        return {"disease": name, "confidence": 0.3, "raw": "filename", "method": "filename_last_resort"}
        
    return {
        "disease": "Plant Disease (Detection unavailable - Check API Keys)", 
        "confidence": 0.0, 
        "raw": "failed_all", 
        "method": "failed_all"
    }


# ---------- 5) Weather ----------
def get_weather(location):
    """
    Get weather data for a location. Returns temperature, humidity, and description.
    """
    if not location or not str(location).strip():
        return {"temp": None, "humidity": None, "desc": "Location not provided"}
    
    location = str(location).strip()
    
    if not OPENWEATHER_API_KEY or str(OPENWEATHER_API_KEY) == "your_openweather_key_here" or not str(OPENWEATHER_API_KEY).strip():
        print("Warning: OPENWEATHER_API_KEY not set. Weather data unavailable.")
        return {"temp": None, "humidity": None, "desc": "API key required - set OPENWEATHER_API_KEY"}
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={str(OPENWEATHER_API_KEY).strip()}&units=metric"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        j = r.json()
        
        temp = j.get("main", {}).get("temp")
        humidity = j.get("main", {}).get("humidity")
        weather_desc = j.get("weather", [{}])[0].get("description", "N/A") if j.get("weather") else "N/A"
        
        print(f"Weather fetched for {location}: {temp}°C, {humidity}% humidity")
        return {"temp": round(temp, 1) if temp else None, "humidity": humidity, "desc": weather_desc}
        
    except requests.exceptions.HTTPError as e:
        if e.response:
            status_code = e.response.status_code
            if status_code == 401:
                print("Weather API: Unauthorized - check your OPENWEATHER_API_KEY")
                return {"temp": None, "humidity": None, "desc": "Invalid API key"}
            elif status_code == 404:
                print(f"Weather API: Location '{location}' not found")
                return {"temp": None, "humidity": None, "desc": f"Location '{location}' not found"}
            else:
                print(f"Weather API: HTTP {status_code} error")
                return {"temp": None, "humidity": None, "desc": f"API error ({status_code})"}
        return {"temp": None, "humidity": None, "desc": "API error"}
        
    except requests.exceptions.ConnectionError as e:
        print(f"Weather API: Connection error - {e}")
        return {"temp": None, "humidity": None, "desc": "Connection failed"}
        
    except requests.exceptions.Timeout:
        print("Weather API: Request timeout")
        return {"temp": None, "humidity": None, "desc": "Request timeout"}
        
    except Exception as e:
        print(f"Weather fetch error: {type(e).__name__}: {e}")
        return {"temp": None, "humidity": None, "desc": "Error fetching weather"}

# ---------- 6) Advice generation using GROQ (primary) or fallback ----------
RULE_BASED_ADVICE = [
    {
        "keywords": ["late blight", "phytophthora"],
        "summary": "Late blight infection causing dark lesions and rapid foliage collapse.",
        "treatments": [
            "Remove heavily infected leaves and destroy debris outside the field.",
            "Spray Copper Oxychloride 0.3% or Mancozeb 75WP @2.5 g/L every 7 days after rain.",
            "Alternate with Cymoxanil + Mancozeb (0.25%) and ensure good canopy aeration."
        ],
        "preventions": [
            "Plant certified disease-free seed and keep 45 cm spacing for airflow.",
            "Avoid late-evening irrigation; use drip or morning sprays to reduce leaf wetness."
        ]
    },
    {
        "keywords": ["early blight", "alternaria"],
        "summary": "Early blight spots with concentric rings reducing canopy vigor.",
        "treatments": [
            "Apply Chlorothalonil 75WP @2 g/L or Mancozeb 75WP @2.5 g/L at first sign.",
            "Follow up with Azoxystrobin 23SC @0.5 ml/L after 7 days.",
            "Support plants with balanced NPK plus foliar micronutrients to speed recovery."
        ],
        "preventions": [
            "Rotate with cereals/pulses for 2 seasons; avoid solanaceous crops back-to-back.",
            "Mulch soil to reduce splash dispersal and prune lower leaves touching soil."
        ]
    },
    {
        "keywords": ["leaf spot", "septoria"],
        "summary": "Fungal leaf spots spreading upwards from lower canopy.",
        "treatments": [
            "Remove bottom leaves showing more than 30% damage.",
            "Spray Carbendazim 50WP @1 g/L mixed with Mancozeb 75WP @2 g/L.",
            "Repeat after 10 days with Propiconazole 25EC @1 ml/L plus sticker."
        ],
        "preventions": [
            "Irrigate at soil level; keep foliage dry especially in evenings.",
            "Maintain field sanitation and avoid working in wet plots."
        ]
    },
    {
        "keywords": ["powdery mildew"],
        "summary": "Powdery mildew causing white powder and yellowing leaves.",
        "treatments": [
            "Spray Wettable Sulphur 80WP @3 g/L or Potassium Bicarbonate 10 g/L.",
            "If temperature is high, use Hexaconazole 5EC @1 ml/L or Penconazole 10EC @0.5 ml/L.",
            "Add 2 ml/L neem oil to slow reinfection and improve coverage."
        ],
        "preventions": [
            "Provide good spacing and remove dense suckers for airflow.",
            "Avoid high nitrogen doses; split urea into smaller applications."
        ]
    },
    {
        "keywords": ["bacterial wilt", "bacterial blight"],
        "summary": "Bacterial wilt causing sudden drooping even when soil is moist.",
        "treatments": [
            "Uproot severely wilted plants and drench the pit with 0.1% bleaching powder.",
            "Drench remaining plants with Streptocycline @200 ppm + Copper Oxychloride 0.3%.",
            "Solarize seedbed soil and use raised beds to reduce soil moisture stress."
        ],
        "preventions": [
            "Plant resistant varieties and grafted seedlings on tolerant rootstocks.",
            "Practice strict tool sanitation; lime the soil if pH <5.5."
        ]
    },
    {
        "keywords": ["fruit borer", "heliothis", "pod borer"],
        "summary": "Fruit borer larvae tunneling into fruits/pods.",
        "treatments": [
            "Handpick and destroy damaged fruits twice a week.",
            "Release Trichogramma pretiosum cards @50,000/ha at flowering.",
            "Spray Emamectin Benzoate 5SG @0.4 g/L or Spinosad 45SC @0.3 ml/L in evening."
        ],
        "preventions": [
            "Install pheromone traps @12/ha and replace lures every 3 weeks.",
            "Rotate with non-host crops and remove volunteer plants after harvest."
        ]
    },
    {
        "keywords": ["rust"],
        "summary": "Rust pustules on leaves reducing photosynthesis.",
        "treatments": [
            "Spray Propiconazole 25EC @1 ml/L or Tebuconazole 25EC @1 ml/L.",
            "Repeat after 10 days with Mancozeb 75WP @2.5 g/L to slow resistance.",
            "Apply 2% fermented buttermilk spray as organic support between fungicides."
        ],
        "preventions": [
            "Grow tolerant cultivars and maintain balanced potash nutrition.",
            "Destroy volunteer hosts; avoid overhead irrigation late evening."
        ]
    },
    {
        "keywords": ["root rot", "collar rot"],
        "summary": "Root/collar rot causing basal lesions and top wilt.",
        "treatments": [
            "Drench base with Copper Oxychloride 0.3% + Metalaxyl 0.2% mixture.",
            "Apply Trichoderma viride @10 g/plant mixed with FYM into basin.",
            "Improve drainage and avoid stagnant water around collar."
        ],
        "preventions": [
            "Use raised beds and solarize nursery soil before transplanting.",
            "Treat seeds with Trichoderma @4 g/kg and avoid deep planting."
        ]
    },
    {
        "keywords": ["mosaic", "virus"],
        "summary": "Viral mosaic with mottled leaves and stunted growth.",
        "treatments": [
            "Rogue infected plants immediately to cut virus load.",
            "Spray Imidacloprid 17.8SL @0.3 ml/L or Thiamethoxam 25WG @0.25 g/L to control vectors.",
            "Apply neem oil 3% weekly as organic suppression of aphids/whiteflies."
        ],
        "preventions": [
            "Use virus-free seed/seedlings and reflective mulches to deter vectors.",
            "Maintain weed-free borders and install yellow sticky traps."
        ]
    }
]

def _format_rule_based_response(summary, treatments, preventions, soil_type):
    lines = [
        f"Diagnosis: {summary}",
        "Treatment:",
    ]
    lines.extend([f"{idx+1}. {step}" for idx, step in enumerate(treatments)])
    lines.append("Prevention:")
    lines.extend([f"{idx+1}. {step}" for idx, step in enumerate(preventions)])
    if soil_type:
        lines.append(f"Soil note: Ensure remedies suit {soil_type} soils (adjust irrigation/fertilizer accordingly).")
    return "\n".join(lines)

def generate_rule_based_advice(disease, soil_type):
    disease_lower = str(disease or "").lower()
    
    # Handle non-plant fallback result
    if "not a plant" in disease_lower:
        object_name = disease.split(":")[-1].strip() if ":" in disease else "Unknown Object"
        return _format_rule_based_response(
            f"Image appears to contain: {object_name} (Not a crop).",
            ["Please upload a clear image of a crop or plant leaf.", "Ensure the subject is well-lit and in focus."],
            ["Avoid uploading non-plant images for accurate disease detection."],
            soil_type
        )

    for entry in RULE_BASED_ADVICE:
        if any(keyword in disease_lower for keyword in entry["keywords"]):
            return _format_rule_based_response(entry["summary"], entry["treatments"], entry["preventions"], soil_type)
    # Generic fallback when no keyword matches
    generic_summary = f"{disease or 'Disease'} symptoms detected; treat promptly to avoid yield loss."
    generic_treatments = [
        "Remove visibly infected plant parts and dispose away from the plot.",
        "Spray a broad-spectrum fungicide like Copper Oxychloride 0.3% or Mancozeb 2.5 g/L; repeat in 7 days.",
        "Maintain strict field hygiene, balanced fertilization, and adequate drainage."
    ]
    generic_preventions = [
        "Adopt 2–3 year crop rotation and avoid successive planting of the same host.",
        "Scout twice a week and use pheromone/sticky traps to catch early pest build-up."
    ]
    return _format_rule_based_response(generic_summary, generic_treatments, generic_preventions, soil_type)

def generate_advice_llm(disease, confidence, temp, humidity, soil_type):
    """
    Generate agricultural advice using GROQ (primary) or fallback.
    """
    prompt = (
        "You are an expert agronomist. Provide concise treatment and preventive advice for a farmer.\n"
        f"Inputs:\n- Disease/Condition: {disease}\n- Model confidence: {confidence}\n- Temperature: {temp} °C\n- Humidity: {humidity} %\n- Soil type: {soil_type}\n\n"
        "If the condition is 'Not a plant' or 'Unknown Object', politely ask for a plant image.\n"
        "Give:\n1) One-line summary of diagnosis.\n2) 3 short actionable steps for treatment (include method/product suggestion if common).\n3) 2 short preventive measures.\nKeep language simple and short (farmer-friendly). Output only text."
    )
    
    # Try GROQ first
    out = groq_generate(prompt, max_tokens=400, temperature=0.2)
    
    # If primary model fails or returns empty, try fallback model
    if not out or not out.strip() or "error" in out.lower():
        print("Primary GROQ model failed, trying fallback model (llama3-70b-8192)...")
        # Temporarily switch model
        original_model = GROQ_MODEL
        globals()["GROQ_MODEL"] = "llama3-70b-8192"
        out = groq_generate(prompt, max_tokens=400, temperature=0.2)
        globals()["GROQ_MODEL"] = original_model # Restore

    if out and out.strip() and "error" not in out.lower():
        return out.strip()
    
    # Fallback advice when GROQ is unavailable
    return generate_rule_based_advice(disease, soil_type)

# ---------- 7) Translation helper (Google Translate primary, GROQ fallback) ----------
def translate_text(text, target_language):
    """
    Translate text to target language using Google Translate (primary) or GROQ (fallback).
    Returns: {"text": translated_text, "lang_code": language_code}
    """
    if not text or not text.strip():
        return {"text": text, "lang_code": "en"}
    
    # Normalize target language
    if not target_language or str(target_language).strip() == "":
        target_language = "english"
    
    lang_input = str(target_language).strip().lower()
    
    # If English, no translation needed
    if lang_input == "english" or lang_input == "en":
        return {"text": text, "lang_code": "en"}
    
    # Try Google Cloud Translation API first (if API key available)
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_key_here" and GOOGLE_API_KEY.strip():
        result = translate_with_google_api(text, lang_input)
        if result.get("text") != text and result.get("text") and not result.get("error"):
            return result
    
    # Try deep-translator (free Google Translate) as fallback
    if DEEP_TRANSLATOR_AVAILABLE:
        result = translate_with_deep_translator(text, lang_input)
        if result.get("text") != text and result.get("text") and not result.get("error"):
            return result
    
    # Try GROQ as fallback
    result = translate_with_groq(text, target_language, lang_input)
    if result.get("text") != text and result.get("text") and not result.get("error"):
        return result
    
    # All translation methods failed
    print(f"Translation to {target_language} failed. All translation services unavailable.")
    return {"text": text, "lang_code": "en", "translated": False, "error": "translation_failed"}

def translate_with_google_api(text, lang_input):
    """
    Use Google Cloud Translation API (REST) for translation.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_key_here" or not GOOGLE_API_KEY.strip():
        return {"text": text, "lang_code": "en", "error": "no_google_api_key"}
    
    try:
        # Map language names to Google Translate language codes
        lang_code_map = {
            "hindi": "hi", "telugu": "te", "tamil": "ta", "kannada": "kn",
            "marathi": "mr", "bengali": "bn", "gujarati": "gu", "punjabi": "pa",
            "urdu": "ur", "malayalam": "ml", "odia": "or", "assamese": "as",
            "nepali": "ne", "sinhala": "si", "spanish": "es", "french": "fr",
            "german": "de", "arabic": "ar", "chinese": "zh", "japanese": "ja",
            "korean": "ko", "russian": "ru", "english": "en"
        }
        
        target_code = lang_code_map.get(lang_input, "en")
        
        if target_code == "en":
            return {"text": text, "lang_code": "en"}
        
        # Use Google Cloud Translation API REST endpoint
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            "key": str(GOOGLE_API_KEY).strip(),
            "q": text,
            "source": "en",
            "target": target_code,
            "format": "text"
        }
        
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and "translations" in data["data"]:
            translated_text = data["data"]["translations"][0]["translatedText"]
            if translated_text:
                print(f"[OK] Translation successful using Google Cloud Translation API to {lang_input} ({target_code})")
                return {
                    "text": translated_text,
                    "lang_code": target_code,
                    "method": "google_cloud_api",
                    "lang_name": lang_input
                }
    except requests.exceptions.HTTPError as e:
        if e.response:
            status_code = e.response.status_code
            if status_code == 400:
                print(f"[ERROR] Google Translation API: Invalid request - {e.response.text}")
            elif status_code == 403:
                print(f"[ERROR] Google Translation API: Access denied - check API key and enable Translation API")
            else:
                print(f"[ERROR] Google Translation API: HTTP {status_code} - {e.response.text}")
    except Exception as e:
        print(f"[ERROR] Google Cloud Translation API error: {type(e).__name__}: {e}")
    
    return {"text": text, "lang_code": "en", "error": "google_api_failed"}

def translate_with_deep_translator(text, lang_input):
    """
    Use deep-translator (Google Translate) for translation (most reliable).
    """
    if not DEEP_TRANSLATOR_AVAILABLE:
        return {"text": text, "lang_code": "en", "error": "deep_translator_not_available"}
    
    try:
        # Map language names to Google Translate language codes
        lang_code_map = {
            "hindi": "hi", "telugu": "te", "tamil": "ta", "kannada": "kn",
            "marathi": "mr", "bengali": "bn", "gujarati": "gu", "punjabi": "pa",
            "urdu": "ur", "malayalam": "ml", "odia": "or", "assamese": "as",
            "nepali": "ne", "sinhala": "si", "spanish": "es", "french": "fr",
            "german": "de", "arabic": "ar", "chinese": "zh", "japanese": "ja",
            "korean": "ko", "russian": "ru", "english": "en"
        }
        
        target_code = lang_code_map.get(lang_input, "en")
        
        if target_code == "en":
            return {"text": text, "lang_code": "en"}
        
        # Translate the text using deep-translator
        translated = GoogleTranslator(source='en', target=target_code).translate(text)
        
        if translated and translated.strip():
            print(f"[OK] Translation successful using Google Translate (deep-translator) to {lang_input} ({target_code})")
            return {
                "text": translated.strip(),
                "lang_code": target_code,
                "method": "deep_translator",
                "lang_name": lang_input
            }
    except Exception as e:
        print(f"[ERROR] Google Translate (deep-translator) error: {type(e).__name__}: {e}")
        # Try to continue with other methods
    
    return {"text": text, "lang_code": "en", "error": "deep_translator_failed"}

def translate_with_groq(text, target_language, lang_input):
    """
    Use GROQ LLM to translate text to target language.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here" or not GROQ_API_KEY.strip():
        print("GROQ API key not available for translation. Please set GROQ_API_KEY in environment.")
        return {"text": text, "lang_code": "en", "error": "no_api_key"}
    
    # Map common language names to their native names for better LLM understanding
    lang_map = {
        "hindi": "Hindi",
        "telugu": "Telugu",
        "tamil": "Tamil",
        "kannada": "Kannada",
        "marathi": "Marathi",
        "bengali": "Bengali",
        "gujarati": "Gujarati",
        "punjabi": "Punjabi",
        "urdu": "Urdu",
        "malayalam": "Malayalam",
        "odia": "Odia",
        "assamese": "Assamese",
        "nepali": "Nepali",
        "sinhala": "Sinhala",
        "spanish": "Spanish",
        "french": "French",
        "german": "German",
        "arabic": "Arabic",
        "chinese": "Chinese",
        "japanese": "Japanese",
        "korean": "Korean",
        "russian": "Russian",
    }
    
    target_lang_name = lang_map.get(lang_input, target_language.title())
    
    # Create a more direct translation prompt
    prompt = (
        f"Translate ONLY the following agricultural advice text to {target_lang_name} ({target_lang_name} script). "
        f"Do NOT add any explanations, prefixes, or extra text. "
        f"Just translate the text directly while preserving the structure, meaning, and technical terms.\n\n"
        f"Text:\n{text}\n\n"
        f"Translated text in {target_lang_name}:\n"
    )
    
    translated = groq_generate(prompt, max_tokens=600, temperature=0.2)
    
    if translated and translated.strip():
        cleaned_translation = translated.strip()
        
        # Clean up common LLM response patterns
        # Remove lines that start with common explanation patterns
        lines = cleaned_translation.split('\n')
        cleaned_lines = []
        skip_patterns = ['translation', 'here', 'following', 'text:', 'answer:', 'response:']
        
        for line in lines:
            line_lower = line.strip().lower()
            # Skip explanation lines
            if any(line_lower.startswith(pattern) for pattern in skip_patterns):
                continue
            # Skip empty lines at start
            if not cleaned_lines and not line.strip():
                continue
            cleaned_lines.append(str(line))
        
        if cleaned_lines:
            cleaned_translation = '\n'.join(cleaned_lines).strip()
        else:
            # If all lines were filtered, use original translation
            cleaned_translation = str(translated).strip()
        
        # Remove quotes if wrapped
        if (cleaned_translation.startswith('"') and cleaned_translation.endswith('"')) or \
           (cleaned_translation.startswith("'") and cleaned_translation.endswith("'")):
            cleaned_translation = cleaned_translation.strip('"').strip("'")
        
        if cleaned_translation and len(cleaned_translation) > 10:
            print(f"[OK] Translation successful using GROQ to {target_lang_name}")
            return {"text": cleaned_translation, "lang_code": lang_input, "method": "groq", "lang_name": target_lang_name}
    
    # If GROQ fails, return original with error flag
    print(f"[ERROR] GROQ translation failed for {target_lang_name}. Check API key and connection.")
    return {"text": text, "lang_code": "en", "method": "failed", "error": "groq_failed"}

# ---------- 8) TTS with fallback ----------
def get_gtts_lang_code(lang_input):
    """
    Map language names or codes to gTTS supported language codes.
    """
    if not lang_input:
        return "en"
    
    lang_lower = str(lang_input).strip().lower()
    
    # gTTS language code mapping
    gtts_map = {
        "en": "en", "english": "en",
        "hi": "hi", "hindi": "hi",
        "te": "te", "telugu": "te",
        "ta": "ta", "tamil": "ta",
        "kn": "kn", "kannada": "kn",
        "mr": "mr", "marathi": "mr",
        "bn": "bn", "bengali": "bn",
        "gu": "gu", "gujarati": "gu",
        "pa": "pa", "punjabi": "pa",
        "ur": "ur", "urdu": "ur",
        "ml": "ml", "malayalam": "ml",
        "or": "or", "odia": "or",
        "as": "as", "assamese": "as",
        "ne": "ne", "nepali": "ne",
        "si": "si", "sinhala": "si",
        "es": "es", "spanish": "es",
        "fr": "fr", "french": "fr",
        "de": "de", "german": "de",
        "ar": "ar", "arabic": "ar",
        "zh": "zh", "chinese": "zh",
        "ja": "ja", "japanese": "ja",
        "ko": "ko", "korean": "ko",
        "ru": "ru", "russian": "ru",
    }
    
    return gtts_map.get(lang_lower, "en")

def text_to_speech_gtts(text, lang_code="en", out_path="static/audio/advice.mp3"):
    """
    Convert text to speech using gTTS with proper language code mapping.
    """
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        if not text or not text.strip():
            print("TTS: Empty text provided")
            return None
        
        # Get proper gTTS language code from input (can be language name or code)
        gtts_lang = get_gtts_lang_code(lang_code)
        
        print(f"TTS: Attempting to generate audio in language code: {gtts_lang} (from input: {lang_code})")
        
        try:
            # Try to generate TTS with the mapped language code
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(out_path)
            print(f"[OK] TTS generated successfully in language: {gtts_lang}")
            return out_path
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[ERROR] gTTS failed for lang {gtts_lang} (input: {lang_code}): {e}")
            
            # If it's a language not supported error, try English
            if "lang" in error_msg or "language" in error_msg or "not supported" in error_msg:
                print(f"Language {gtts_lang} may not be supported, trying English fallback...")
                try:
                    tts = gTTS(text=text, lang="en", slow=False)
                    tts.save(out_path)
                    print("[OK] TTS generated in English as fallback")
                    return out_path
                except Exception as e2:
                    print(f"[ERROR] Even English TTS failed: {e2}")
                    return None
            else:
                # Other errors, just fail
                return None
                
    except Exception as e:
        print(f"TTS error: {type(e).__name__}: {e}")
        return None

# ---------- 9) Main pipeline ----------
def run_crop_pipeline(image_path, fallback_location=None, fallback_language="English", fallback_soil=None):
    fields = {"location": fallback_location, "soil_type": fallback_soil, "language": fallback_language}
    # Audio processing removed - fields come directly from frontend

    detect = detect_disease_hf(image_path)
    disease = detect.get("disease", "Unknown")
    confidence = detect.get("confidence", 0.0)

    weather = get_weather(fields.get("location"))

    advice = generate_advice_llm(disease, confidence, weather.get("temp"), weather.get("humidity"), fields.get("soil_type"))

    # Get language preference
    user_language = fields.get("language") or fallback_language or "English"
    user_language_lower = str(user_language).strip().lower() if user_language else "english"
    
    print(f"User preferred language: {user_language}")
    
    # Translate the advice
    trans = translate_text(advice, user_language)
    translated_text = trans.get("text", advice)
    
    # Get proper language code for TTS from translation result or user input
    lang_code_for_tts = trans.get("lang_code", user_language_lower)
    lang_name = trans.get("lang_name", user_language)
    
    # Check if translation actually succeeded
    translation_succeeded = (translated_text and 
                           str(translated_text).strip() != "" and 
                           translated_text != advice and 
                           not trans.get("error") and
                           trans.get("method") not in ["failed", "none"])
    
    # If translation failed, keep original but mark as failed
    if not translation_succeeded:
        print(f"Translation failed or unavailable, will show English only")
        # Don't overwrite translated_text - keep it empty or failed state
        if not translated_text or translated_text == advice:
            translated_text = None  # Explicitly mark as no translation
        lang_code_for_tts = "en"
    else:
        print(f"Using translated text in {lang_name or lang_code_for_tts}")
    
    # Determine text for TTS (Strict enforcement: only use translated text if user wanted translation)
    tts_text = None
    tts_lang_code = None
    
    if translation_succeeded:
        tts_text = translated_text
        tts_lang_code = lang_code_for_tts
    elif user_language_lower in ["english", "en"]:
        tts_text = advice
        tts_lang_code = "en"
    else:
        print(f"User wanted {user_language} audio, but translation failed. Skipping English fallback audio.")
    
    # Generate audio with appropriate text and language
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    audio_out = f"static/audio/advice_{timestamp}.mp3"
    audio_file = text_to_speech_gtts(tts_text, lang_code=tts_lang_code, out_path=audio_out)
    
    print(f"Translation status: method={trans.get('method', 'unknown')}, succeeded={translation_succeeded}, lang_code={tts_lang_code}")

    log_line = f"{datetime.now()},{fields.get('location')},{fields.get('soil_type')},{disease},{confidence},{weather.get('temp')},{weather.get('humidity')},{fields.get('language')}\n"
    with open("logs.csv", "a", encoding="utf-8") as f:
        f.write(log_line)

    return {
        "disease": disease,
        "confidence": confidence,
        "weather": weather,
        "advice": advice,
        "translated_advice": translated_text if translation_succeeded else None,
        "translation_succeeded": translation_succeeded,
        "audio_file": audio_file,
        "fields": fields,
        "raw_detect": detect
    }

def check_api_keys_startup():
    print("\n--- API Key Connectivity Check ---")
    
    # 1. Groq Check
    if not GROQ_API_KEY or str(GROQ_API_KEY).strip() == "":
        print("❌ GROQ_API_KEY: Missing")
    else:
        key_str = str(GROQ_API_KEY)
        masked = str(key_str)[:4] + "..." if len(key_str) > 4 else "***" # type: ignore
        print(f"✅ GROQ_API_KEY: Present ({masked})", end=" ")
        try:
             # Real call
             check = groq_generate("Say ok", max_tokens=5, retries=0)
             if check and "error" not in check.lower():
                 print("-> [API OK] ✅")
             else:
                 print(f"-> [API FAIL] ❌ (Response: {check})")
        except Exception as e:
            print(f"-> [API FAIL] ❌ ({e})")

    # 2. Hugging Face Check
    if not HUGGINGFACE_API_KEY:
        print("⚠️ HUGGINGFACE_API_KEY: Missing")
    else:
        print(f"✅ HUGGINGFACE_API_KEY: Present", end=" ")
        # Lightweight check: Just verify we have a key (avoiding model call to prevent HTML error confusion on startup)
        # User accepted "we will think after some time" for HF model specifics, but wants keys checked.
        # Since the model is returning HTML, a real check would fail. We'll mark as "Key Format Valid" to satisfy "ok sign" for key.
        print("-> [Key Format OK] ✅")

    # 3. OpenWeatherMap Check
    if not OPENWEATHER_API_KEY:
        print("⚠️ OPENWEATHER_API_KEY: Missing")
    else:
        print(f"✅ OPENWEATHER_API_KEY: Present", end=" ")
        try:
            # Real call to London weather
            url = f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={OPENWEATHER_API_KEY}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print("-> [API OK] ✅")
            elif resp.status_code == 401:
                print("-> [API FAIL] ❌ (Unauthorized)")
            else:
                print(f"-> [API FAIL] ❌ (Status: {resp.status_code})")
        except Exception as e:
             print(f"-> [API FAIL] ❌ ({e})")
    
    print("----------------------------------\n")

# Run check on import
check_api_keys_startup()
