import React, { useRef, useState } from "react";

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunks = useRef([]);
  const audioRef = useRef(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: "audio/webm", // ✅ record as webm then convert on server
    });

    mediaRecorderRef.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data);
    };

    mediaRecorderRef.current.onstop = async () => {
      setLoading(true);
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      chunks.current = [];

      const formData = new FormData();
      formData.append("audio", blob, "recorded_audio.webm");

      try {
        // 1⃣ Transcribe audio to text
        const res1 = await fetch("http://localhost:5000/api/audio", {
          method: "POST",
          body: formData,
        });
        const { text, filename: userAudio } = await res1.json();
        console.log("🎤 Extracted text:", text);

        // 2⃣ Send text to LLM (e.g., Ollama)
        const res2 = await fetch("http://localhost:5000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const { reply } = await res2.json();
        console.log("🤖 AI Reply:", reply);

        // 3⃣ Convert reply to WAV
        const res3 = await fetch("http://localhost:5000/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: reply }),
        });
        const { filename: ttsFilename } = await res3.json();

        // 4⃣ Generate lipsync JSON from WAV
        await fetch("http://localhost:5000/api/lipsync", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: ttsFilename }),
        });

        // 5⃣ Play audio
        const audioURL = `http://localhost:5000/temp/${ttsFilename}`;
        audioRef.current.src = audioURL;
        audioRef.current.play();
      } catch (err) {
        console.error("❌ Error during recording and processing:", err);
      } finally {
        setLoading(false);
      }
    };

    mediaRecorderRef.current.start();
    setRecording(true);

    // 🕐 Record for 5 seconds
    setTimeout(() => {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }, 5000);
  };

  return (
    <div>
      <button onClick={startRecording} disabled={recording || loading}>
        {recording
          ? "🎙️ Recording..."
          : loading
          ? "⏳ Processing..."
          : "🎤 Record your voice"}
      </button>
      <audio ref={audioRef} controls style={{ marginTop: "10px" }} />
    </div>
  );
};

export default AudioRecorder;
