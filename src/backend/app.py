from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import shutil

from transcribe import transcribe_audio
from generate_tts import generate_tts
from generate_lipsync import generate_lipsync
from backend.agent_utils import get_agent  # ✅ مضاف لتحليل CSV
from langchain.chat_models import ChatOpenAI  # ✅ GPT

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or "sk-xxx"  # ضع توكنك هنا

# ✅ New: Replace Ollama with GPT for Chat
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')

    try:
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.4, openai_api_key=OPENAI_API_KEY)
        result = llm.predict(user_input)
        return jsonify({"reply": result})
    except Exception as e:
        print("❌ Chat Error:", e)
        return jsonify({"reply": "⚠️ Unexpected error"}), 500

# ✅ New: Ask CSV using GPT + LangChain
@app.route('/api/ask-csv', methods=['POST'])
def ask_csv():
    data = request.get_json()
    question = data.get('question', '')

    try:
        agent = get_agent()
        response = agent.run(question)
        return jsonify({"response": response})
    except Exception as e:
        print("❌ CSV Agent Error:", e)
        return jsonify({"response": "⚠️ Failed to answer."}), 500

# ✅ Convert audio to text
@app.route("/api/audio", methods=["POST"])
def audio_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    filename = f"recording_{int(datetime.now().timestamp())}.webm"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(file_path)

    try:
        text = transcribe_audio(file_path)
        return jsonify({"text": text, "filename": filename})
    except Exception as e:
        print("❌ Audio Error:", e)
        return jsonify({"error": "Failed to transcribe audio"}), 500

# ✅ Generate TTS and save as a fixed name
@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Text is missing"}), 400

    current_wav = os.path.join(UPLOAD_FOLDER, "current.wav")

    try:
        generate_tts(text, current_wav)
        return jsonify({"audio_path": "/temp/current.wav", "filename": "current.wav"})
    except Exception as e:
        print("❌ TTS Error:", e)
        return jsonify({"error": "Failed to generate audio"}), 500

# ✅ Generate lipsync and save as current.json
@app.route('/api/lipsync', methods=['POST'])
def lipsync():
    data = request.get_json()
    wav_filename = data.get('filename', '')
    if not wav_filename:
        return jsonify({"error": "Audio filename is missing"}), 400

    wav_path = os.path.join(UPLOAD_FOLDER, wav_filename)

    try:
        output_json_path = generate_lipsync(wav_path)
        target_path = os.path.join(UPLOAD_FOLDER, "current.json")

        if os.path.abspath(output_json_path) != os.path.abspath(target_path):
            shutil.copy(output_json_path, target_path)

        return jsonify({
            "json_path": "/temp/current.json",
            "audio_path": "/temp/current.wav"
        })
    except Exception as e:
        print("❌ Lipsync Error:", e)
        return jsonify({"error": "Failed to generate lipsync"}), 500

# ✅ Serve static files from /temp
@app.route('/temp/<path:filename>')
def serve_temp_file(filename):
    return send_from_directory("temp", filename)

# ✅ Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
