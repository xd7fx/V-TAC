import edge_tts
import asyncio
import os

def generate_tts(text, output_path="temp/current.wav"):
    if not text.strip():
        raise ValueError("❌ Cannot convert empty text to speech")

    try:
        asyncio.run(generate_tts_async(text, output_path))
    except Exception as e:
        print("❌ TTS sync error:", e)
        raise e


async def generate_tts_async(text, output_path):
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-GuyNeural"  # ✅ Male American voice
        )
        await communicate.save(output_path)
        print("✅ Audio saved successfully:", output_path)

        if not os.path.exists(output_path):
            raise FileNotFoundError("❌ Audio file was not created.")

    except Exception as e:
        print("❌ TTS async error:", e)
        raise e
