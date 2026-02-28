# AI Crop Disease Detection & Advisory Agent (GROQ Llama 3.3.70B)

This is a production-style demo application for crop disease detection and agricultural advisory using AI agents.

## Features

- **Image Disease Detection** via Hugging Face Inference API (Default: `Daksh159/plant-disease-mobilenetv2`)
- **Robust Fallback System**:
    - **Vision Fallback**: Uses Llama-3.2-11b-vision (if available) to describe images when disease detection fails.
    - **Smart Metadata Analysis**: Uses Llama-3.3-70b-versatile to generate professional diagnoses from filenames if visual APIs are down.
- **LLM Tasks** (parsing, advice generation, translation) via Llama-3.3-70b-versatile on GROQ
- **Weather Data** via OpenWeatherMap API
- **Speech-to-Text (STT)** via SpeechRecognition (Google Web Speech API)
- **Translation** via `deep-translator` (Google Translate wrapper) with Groq fallback
- **Text-to-Speech (TTS)** via gTTS (Google Text-to-Speech)

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for pydub audio processing)
  - Windows: Download from https://ffmpeg.org/download.html or use `choco install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crop-ai-agent-repo
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```
   
   **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_key_here
   HUGGINGFACE_API_KEY=your_hf_token_here
   HUGGINGFACE_MODEL=Daksh159/plant-disease-mobilenetv2
   OPENWEATHER_API_KEY=your_openweather_key_here
   PORT=3000
   ```
   
   **Get API Keys:**
   - GROQ API: https://console.groq.com/
   - Hugging Face: https://huggingface.co/settings/tokens
   - OpenWeatherMap: https://openweathermap.org/api

5. **Verify API keys (optional)**
   ```bash
   python check_api.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   
   The app will be available at `http://localhost:3000`

## Usage

1. Open the web interface at `http://localhost:3000`
2. Upload a crop/leaf image (required)
3. Optionally upload a voice note with location, soil type, and preferred language
4. Or fill in the form fields manually:
   - Location (e.g., "Hyderabad")
   - Soil Type (e.g., "loam", "clay", "sandy")
   - Preferred Language (e.g., "English", "Telugu", "Hindi", "Spanish")
5. Click "Analyze" to get disease detection and agricultural advice

## Project Structure

```
crop-ai-agent-repo/
├── app.py                 # Flask web application
├── autogen_agents.py      # Main pipeline logic (disease detection, advice, translation)
├── check_api.py           # API key verification script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── logs.csv               # Analysis logs
├── uploads/               # Uploaded images and audio files
├── static/
│   └── audio/            # Generated TTS audio files
└── templates/
    ├── index.html        # Main upload form
    └── result.html       # Results display page
```

## API Requirements

- **GROQ_API_KEY**: Required for LLM tasks (advice generation, translation, transcript parsing)
- **HUGGINGFACE_API_KEY**: Required for disease detection (image classification)
- **OPENWEATHER_API_KEY**: Required for weather data (temperature, humidity)

Note: The application has fallback mechanisms if some APIs are unavailable, but functionality will be limited.

## Supported Languages

The system supports translation and TTS in multiple languages including:
English, Hindi, Telugu, Tamil, Kannada, Marathi, Bengali, Gujarati, Punjabi, Urdu, Malayalam, Odia, Assamese, Nepali, Sinhala, Spanish, French, German, Arabic, Chinese, Japanese, Korean, Russian, and more.

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **Audio processing errors**: Ensure FFmpeg is installed and in your system PATH
- **API errors**: 
    - Verify your API keys using `python check_api.py`.
    - If you see "HTML instead of JSON" or 400/401 errors, the API might be down or your key might have limits.
    - **Don't Worry**: The app has a smart fallback that will still give you a result based on your file's name/metadata.
- **Port already in use**: Change the PORT in `.env` or set it as an environment variable

## License

This project is provided as-is for educational and demonstration purposes.



