# Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Install FFmpeg (Required for Audio Processing)

**Windows:**
- Download from https://ffmpeg.org/download.html
- Or use Chocolatey: `choco install ffmpeg`
- Add FFmpeg to your system PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Step 3: Set Up Environment Variables

1. Copy `ENV_TEMPLATE.txt` to `.env`:
   ```bash
   # Windows PowerShell
   Copy-Item ENV_TEMPLATE.txt .env
   
   # Linux/macOS
   cp ENV_TEMPLATE.txt .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   GROQ_API_KEY=your_actual_groq_key
   HUGGINGFACE_API_KEY=your_actual_hf_token
   OPENWEATHER_API_KEY=your_actual_weather_key
   ```

## Step 4: Verify API Keys

```bash
python check_api.py
```

You should see `[OK] SET` for all API keys you've configured.

## Step 5: Run the Application

```bash
python app.py
```

The app will start at `http://localhost:3000`

## Step 6: Test the Application

1. Open `http://localhost:3000` in your browser
2. Upload a crop/leaf image
3. Optionally upload an audio file or fill in the form
4. Click "Analyze"

## Troubleshooting

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Audio Processing Errors
- Verify FFmpeg is installed: `ffmpeg -version`
- Make sure FFmpeg is in your system PATH

### API Errors
- Run `python check_api.py` to verify API keys
- Check that your API keys are correct in `.env`
- Ensure you have internet connection

### Port Already in Use
- Change the PORT in `.env` or set it as environment variable
- Or kill the process using port 3000

## Getting API Keys

1. **GROQ API Key:**
   - Visit https://console.groq.com/
   - Sign up/login
   - Create an API key
   - Copy to `.env` as `GROQ_API_KEY`

2. **Hugging Face API Key:**
   - Visit https://huggingface.co/settings/tokens
   - Sign up/login
   - Create a new token (read access is enough)
   - Copy to `.env` as `HUGGINGFACE_API_KEY`

3. **OpenWeatherMap API Key:**
   - Visit https://openweathermap.org/api
   - Sign up for free account
   - Get your API key
   - Copy to `.env` as `OPENWEATHER_API_KEY`

## Project Status

✅ All dependencies installed and verified
✅ Code improvements applied
✅ Error handling enhanced
✅ Temporary file cleanup fixed
✅ Documentation updated

## Next Steps

1. Review `IMPROVEMENTS.md` for suggested enhancements
2. Test with real crop images
3. Configure production settings if deploying
4. Consider implementing additional features from improvements document

