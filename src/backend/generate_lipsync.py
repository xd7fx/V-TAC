import subprocess
import os

def generate_lipsync(input_audio_path):
    temp_dir = os.path.dirname(input_audio_path)
    
    # ✅ Save the temporary audio under a different name
    fixed_audio_path = input_audio_path.replace(".wav", "_converted.wav")
    output_json_path = input_audio_path.replace(".wav", ".json")

    # ✅ Relative path to rhubarb based on the updated structure
    rhubarb_path = os.path.join(os.path.dirname(__file__), "bin", "rhubarb.exe")

    # ✅ Convert to PCM WAV
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_audio_path,
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        fixed_audio_path
    ], check=True)

    # ✅ Generate lipsync
    subprocess.run([
        rhubarb_path,
        "-r", "phonetic",
        "-f", "json",
        "-o", output_json_path,
        fixed_audio_path
    ], check=True)

    return output_json_path
