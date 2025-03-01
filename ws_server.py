from flask import Flask, request, jsonify, render_template
import whisper
from pydub import AudioSegment
import os
from googletrans import Translator, LANGUAGES

app = Flask(__name__)

# Load Whisper Model
model = whisper.load_model("tiny")
translator = Translator()

# Ensure 'uploads' directory exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to transcribe audio
def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

# API Endpoint: Get available languages
@app.route("/languages", methods=["GET"])
def get_languages():
    return jsonify({"languages": LANGUAGES})

# API Endpoint: Upload and transcribe audio
@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_ext = file.filename.split(".")[-1]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Convert to WAV if needed
    if file_ext.lower() != "wav":
        audio = AudioSegment.from_file(file_path)
        new_file_path = file_path.rsplit(".", 1)[0] + ".wav"
        audio.export(new_file_path, format="wav")
        os.remove(file_path)  # Remove original file
        file_path = new_file_path  # Use new converted file

    # Transcribe the audio
    text = transcribe_audio(file_path)
    
    return jsonify({"text": text})

# API Endpoint: Translate text
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.json
    text = data.get("text")
    target_lang = data.get("lang")

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if not target_lang:
        return jsonify({"error": "No target language provided"}), 400

    try:
        translated_text = translator.translate(text, dest=target_lang).text
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Web Interface
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
