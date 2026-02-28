import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from autogen_agents import run_crop_pipeline
from dotenv import load_dotenv
load_dotenv()


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3', 'm4a'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        image_file = request.files.get('image')
        # Audio file upload removed in favor of direct speech-to-text
        
        fallback_location = request.form.get("location") or None
        fallback_language = request.form.get("language") or "English"
        fallback_soil = request.form.get("soil_type") or None

        if not image_file or image_file.filename == "":
            return "Please upload an image file", 400
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        else:
            return "Invalid image file type", 400

        # call pipeline (audio_path removed)
        result = run_crop_pipeline(image_path, fallback_location, fallback_language, fallback_soil)

        audio_url = result.get("audio_file")
        audio_url = "/" + audio_url.replace("\\", "/") if audio_url else None

        return render_template("result.html", result=result, image_path="/" + image_path.replace("\\","/"), audio_url=audio_url)
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in analyze route: {error_msg}")
        traceback.print_exc()
        # Return user-friendly error message
        return f"An error occurred while processing your request: {error_msg}. Please try again or contact support.", 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/test_result")
def test_result():
    # Mock result for testing UI
    mock_result = {
        "disease": "Tomato Early Blight",
        "confidence": "95.5%",
        "advice": "Treat with fungicides containing mancozeb or chlorothalonil. Remove infected leaves immediately to prevent spread. Ensure proper air circulation between plants.",
        "translated_advice": "Mancozeb (మాంకోజెబ్) లేదా chlorothalonil (క్లోరోథలోనిల్) కలిగిన శిలీంద్రనాశకాలతో చికిత్స చేయండి. వ్యాప్తిని నివారించడానికి సోకిన ఆకులను వెంటనే తొలగించండి. మొక్కల మధ్య సరైన గాలి ప్రసరణను నిర్ధారించుకోండి.",
        "fields": {
            "soil_type": "Loamy Soil",
            "location": "Hyderabad, Telangana",
            "language": "Telugu"
        },
        "weather": {
            "temp": 28,
            "humidity": 65
        },
        "audio_file": "static/audio/test_audio.mp3"
    }
    return render_template("result.html", result=mock_result, image_path="/static/css/style.css", audio_url=None) # Using style.css as dummy image

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
