import os
import subprocess
from transformers import pipeline

# Initialize the ASR pipeline
asr = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h")

def transcribe_audio(audio_path):
    print(f"🔍 Converting file: {audio_path}")
    wav_path = audio_path.replace(".webm", ".wav")

    try:
        # Convert to WAV with 16kHz mono using ffmpeg
        subprocess.run([
            "bin/ffmpeg.exe", "-y", "-i", audio_path,
            "-ar", "16000", "-ac", "1", wav_path
        ], check=True)
        print("✅ Audio successfully converted to WAV:", wav_path)
    except Exception as e:
        print("❌ Failed to convert to WAV:", e)
        raise e

    try:
        # Run transcription
        result = asr(wav_path)
        raw_text = result["text"]
        print("✅ Raw transcription:", raw_text)

        cleaned_text = raw_text.lower().strip().capitalize()
        print("✅ Cleaned transcription:", cleaned_text)

        return cleaned_text
    except Exception as e:
        print("❌ Transcription failed:", e)
        raise e
    finally:
        try:
            os.remove(wav_path)
        except:
            pass
