# AI Crop Doctor: An Intelligent, Multilingual, and Context-Aware Plant Disease Diagnostics and Advisory System

**Abstract**—*Agriculture forms the backbone of the global economy, yet crop diseases continuously threaten food security and farmer livelihoods. Timely, accurate, and accessible diagnosis is critical for effective crop management. This paper presents the "AI Crop Doctor," a robust, web-based artificial intelligence system designed to automatically identify plant diseases, assess real-time environmental conditions, and generate localized, actionable agricultural advice. The system employs a multi-tiered fallback architecture to ensure high reliability, utilizing a local PyTorch MobileNetV2 model for primary disease classification, backed by cloud-based Vision Large Language Models (LLMs) such as GROQ's Llama 3.2 Vision. Furthermore, contextual insights are gathered via the OpenWeatherMap API, while Agronomist Advice is dynamically generated using the GROQ Llama 3.3 70B model. To bridge the digital divide, the system integrates a multilingual interface powered by deep-translator and Google Text-to-Speech (gTTS), enabling voice-based accessible outputs for farmers in their native languages. This paper details the complete technology stack, module functions, integration architecture, and intelligent automated fallback mechanisms ensuring 100% uptime for advisory generation.*

**Keywords**—*Precision Agriculture, Plant Disease Detection, MobileNetV2, Large Language Models (LLMs), Llama 3, Multilingual Advisory System, Fallback Architecture.*

---

## I. INTRODUCTION

Crop diseases cause substantial yield losses globally, severely impacting smallholder farmers who lack immediate access to expert agricultural extension officers or agronomists. Traditional disease identification relies on visual inspection by experts, which is time-consuming, expensive, and subject to human error. With the advent of computer vision and natural language processing (NLP), automated intelligent systems have emerged to democratize access to agricultural expertise. 

This paper outlines the development of the **AI Crop Doctor**, an end-to-end web application that takes user-provided images of crops, assesses their health, and yields comprehensive, localized treatment plans. The key innovation in this proposed system lies in its robust multi-layered fallback pipeline, ensuring fault tolerance and uninterrupted service even when primary predictive models or external APIs fail. 

## II. SYSTEM ARCHITECTURE AND TECHNOLOGY STACK

The AI Crop Doctor follows a client-server architecture, intertwining modern web technologies with advanced deep learning models and API services. 

### A. Frontend (User Interface)
The frontend serves as the primary data ingestion point. It is built using:
1. **HTML5 & CSS3:** For structuring and styling a responsive, user-friendly dashboard capable of running on mobile devices.
2. **Vanilla JavaScript & Device APIs:** Facilitates client-side logic, asynchronous file uploads, and loading screen management. Two primary browser APIs are integrated to eliminate typing barriers:
   - **HTML5 Geolocation API:** The system automatically requests user coordinates (Latitude/Longitude) upon page load. Once permitted, these coordinates are piped via an asynchronous fetch call directly to the OpenWeather Reverse Geocoding API to seamlessly extract the user's City and Country. 
   - **Web Speech API:** Allows users with limited digital literacy to dictate their location or preferred language directly via a microphone.
3. **Dynamic Visual Elements:** The UI replaces standard text boxes with highly accessible image-based selection drop-downs. Most notably, the *Soil Type* selector displays real textural images (generated dynamically via AI) of all eight primary Indian soil types, ranging from Alluvial to Peaty & Marshy soils.

### B. Backend Framework
1. **Python (3.8+):** Serves as the core programming language handling logic, system I/O, and API integrations.
2. **Flask (`app.py`):** A lightweight WSGI web application framework defining the server routes. It receives the `POST` request payloads containing the crop image and metadata (location, soil, language), safely stores the image in an `uploads/` directory, and delegates processing to the central AI Agent Pipeline (`autogen_agents.py`).

## III. AI MODELS, MODULES, AND WORKFLOW

The central intelligence of the project is organized into heavily decoupled but sequential modules. Below is a detailed description of each module, the specific models or libraries running within them, their individual responsibilities, and the fallback logic.

### Module A: Disease Detection Phase (The Vision Agent)
The system attempts to classify the crop disease using a sophisticated 3-tier cascade approach to guarantee a diagnostic result.

1. **Primary Agent (Local PyTorch MobileNetV2):** 
   - **Model Details:** A Convolutional Neural Network (CNN) architecture optimized for mobile and low-latency environments (MobileNetV2), trained specifically on plant disease datasets (`mobilenetv2_plant.pth` / `Daksh159/plant-disease-mobilenetv2`). 
   - **Functionality:** It processes the image using `torchvision.transforms` (resizing to 224x224, normalizing pixel values) and passes it through the model. It supports classifying across 38 distinct plant-disease combinations, including Apple Scab, Tomato Late Blight, and healthy foliage.
   - **Library:** `PyTorch` (`torch`, `torch.nn`, `torchvision`).

2. **First Fallback (GROQ Llama 3.2 Vision API):**
   - **Trigger:** Initiated if the local PyTorch model is uninstalled or fails to load.
   - **Model Details:** Llama 3.2 Vision (90B parameters) accessed via the GROQ API.
   - **Functionality:** The image is base64 encoded and sent to GROQ with a system prompt instructing the model to act as a plant pathologist. The LLM conducts a zero-shot visual analysis, detecting the disease or noting if the image is unrelated to plants.

3. **Second Fallback (Metadata Analysis using GROQ Text):**
   - **Trigger:** Executed if the Vision API experiences an outage or timeout.
   - **Model Details:** GROQ Llama Text Model.
   - **Functionality:** It uses the uploaded file’s name (e.g., `tomato_blight.jpg`) to cleverly deduce the intended crop and disease context using NLP techniques and regex, ensuring that the pipeline never halts.

### Module B: Context Gathering (The Weather & Geographic Agent)
Agricultural treatments depend heavily on climatic states.
1. **Libraries & APIs:** `requests` module interfacing with the **OpenWeatherMap API**, supported by client-side browser GPS.
2. **Functionality:** 
   - **Geographic Translation:** As described in Section II-A, explicit city names are extracted losslessly from precise user coordinates via reverse geocoding.
   - **Atmospheric Extraction:** Supplying the location string, this module fetches real-time temperature (°C), humidity (%), and weather descriptions. This provides the generative LLM crucial context for accurate chemical treatment recommendations (e.g., modifying fungicide advice if it is currently raining or highly humid).

### Module C: Agronomist Advice Generation
Once the disease string, weather context, and soil type are confirmed, the system prescribes treatments.
1. **Primary Agent (GROQ Llama 3.3 70B Versatile):**
   - **Model Details:** A state-of-the-art 70-billion parameter generative language model accessed via the GROQ API.
   - **Functionality:** Driven by an advanced prompt, the LLM assumes the persona of an expert agronomist. It consumes the diagnosis, confidence score, weather, and **soil classifier** (one of the eight structural types native to the Indian subcontinent: Alluvial, Red, Black, Laterite, Arid, Mountain, Alkaline, or Peaty), outputting:
     - A 1-line diagnostic summary.
     - 3 actionable treatment steps (including specific chemical or organic solutions).
     - 2 preventative measures tailored to avoid future environmental or soil-borne triggers.
     - Predictive analytics on secondary diseases prone to occur under current weather conditions.
2. **First Fallback (Alternative GROQ Model):** Switches to `llama3-70b-8192` if the primary model fails.
3. **Second Fallback (Rule-Based Expert System):** If all LLMs fail, the system queries a hardcoded Python dictionary mapping disease keywords (e.g., "blight", "rust", "powdery mildew") to standard, verified agricultural treatments.

### Module D: Translation & Localization
To support global farmers, the generated English advice must be natively understood.
1. **Libraries/Tools:** `deep-translator` (Google Translator), `googletrans`, and Google Cloud Translation API.
2. **Functionality:** The system dynamically normalizes the demanded language (e.g., Hindi, Telugu, Marathi). 
   - It first attempts translation using Google's rapid machine translation APIs.
   - If limits are reached, the module falls back to asking the GROQ LLM to perform language-to-language translation without sacrificing context.

### Module E: Text-to-Speech (The Speaker Agent)
Accessible UI requires accommodating users with low literacy.
1. **Library:** `gTTS` (Google Text-to-Speech).
2. **Functionality:** The fully translated text is fed into the gTTS engine, generating a localized synthetic VoIP MP3 audio file. This file is saved to a static directory.
3. **Frontend Integration:** The resulting HTML response exposes a simple audio player allowing the farmer to push "play" and listen to the advice dynamically.

### Module F: Data Logging (Analytics Module)
1. **Library:** Native Python `csv` handling.
2. **Functionality:** Every prediction cycle silently logs timestamp, user location, detected disease, model confidence, local weather, and language into a `logs.csv` file. This establishes a robust backend data pool for agronomists to perform future disease outbreak tracking or dashboard analytics.

## IV. PROCESS WORKFLOW

1. **User Initiation:** A farmer accesses `/index.html`. The app silently proxies their GPS coordinates into a City format. They visually select their soil texture (from 8 specific classifications) and upload a leaf image. Both are securely posted to `/analyze`.
2. **Pipeline Trigger:** Flask invokes `run_crop_pipeline()` inside `autogen_agents.py`.
3. **Vision Processing:** The Local CNN (MobileNetV2) or Vision LLM extracts the disease name.
4. **Context Injection:** OpenWeatherMap API pulls live climate data.
5. **Generative Assessment:** The GROQ LLM fuses the disease and weather to author a custom agronomic report.
6. **Localization Post-Processing:** The report translates into the user’s mother tongue, and an MP3 voice file is simultaneously rendered.
7. **Delivery:** Values are securely funneled via Flask templating into `result.html`, presenting a complete, multilingual readable and playable diagnostic profile to the farmer.

## V. CONCLUSION

The AI Crop Doctor demonstrates a sophisticated convergence of edge-based deep learning (PyTorch), high-scale cloud-based generative AI (GROQ Llama3), context-aware API integrations (OpenWeatherMap), and accessibility-focused NLP tools. Its primary strength lies in its fault-tolerant, resilient fallback architectures, ensuring that the farmer consistently receives vital diagnostic insights and treatment advice irrespective of fluctuating network or service environments. Such scalable precision agriculture tools possess immense potential to maximize crop yields, augment agricultural extension services, and empower farming communities worldwide.

## REFERENCES
[1] Howard, A. G., et al. "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications," arXiv preprint arXiv:1704.04861, 2017.
[2] Meta AI, "Llama 3 Foundation Models," Technical Report, 2024. [Online Access: https://ai.meta.com/llama/]
[3] PyTorch Core Team, "PyTorch: An Imperative Style, High-Performance Deep Learning Library," Advances in Neural Information Processing Systems 32, 2019.
[4] "OpenWeatherMap API Documentation", OpenWeather. [Online]. Available: https://openweathermap.org/api
[5] Flask Framework Documentation. Pallets Projects. [Online]. Available: https://flask.palletsprojects.com/
