import React, { useState, useRef, useEffect } from "react";
import "./../style.css";
import { Canvas } from "@react-three/fiber";
import { Experience } from "./Experience";
import ChatBot from "./ChatBot";
import CsvAgentQA from "./CsvAgentQA"; // ✅ تمت إضافته

const CustomLayout = () => {
  const [playAudio, setPlayAudio] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [newMessage, setNewMessage] = useState("");
  const chunks = useRef([]);
  const mediaRecorder = useRef(null);

  useEffect(() => {
    if (playAudio?.script) {
      console.log("🎧 Playing audio for script:", playAudio.script);
    }
  }, [playAudio]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorder.current = recorder;
      chunks.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunks.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", blob, "recorded_audio.webm");

        try {
          const response = await fetch("http://localhost:5000/api/audio", {
            method: "POST",
            body: formData,
          });
          const { text } = await response.json();
          if (!text) throw new Error("❌ Speech-to-text failed");

          setNewMessage(text);
        } catch (error) {
          console.error("❌ Error during audio transcription:", error);
        }
      };

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("🎤 Error starting recording:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
      mediaRecorder.current.stop();
      setIsRecording(false);
    } else {
      console.warn("⚠️ No active recording.");
    }
  };

  return (
    <div className="container">
      <div className="left">
        <div className="box tall" id="box1">
          <Canvas
            shadows
            camera={{ position: [0, 1.4, 3], fov: 30 }}
            style={{
              width: "100%",
              height: "100%",
              borderRadius: "12px",
              overflow: "hidden",
              display: "block",
            }}
          >
            <color attach="background" args={["#ececec"]} />
            <Experience
              playAudio={playAudio?.playAudio}
              script={playAudio?.script}
            />
          </Canvas>
        </div>

        <div className="box short" id="box2">
          <div className="button-row">
            <button
              className="play-button"
              onClick={startRecording}
              disabled={isRecording}
            >
              🎤 Start Recording
            </button>
            <button
              className="stop-button"
              onClick={stopRecording}
              disabled={!isRecording}
            >
              🛑 Stop
            </button>
          </div>
        </div>
      </div>

      <div className="right">
        <div className="top-boxes">
          <div className="box small" id="box3">
            <CsvAgentQA /> {/* ✅ إدراج واجهة تحليل CSV */}
          </div>
          <div className="box small" id="box4"></div>
        </div>
        <div className="box wide" id="box5">
          <ChatBot
            inputOverride={newMessage}
            onBotReply={(scriptName) => {
              console.log("🧠 Bot reply ready:", scriptName);
              setPlayAudio({ playAudio: true, script: scriptName });
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default CustomLayout;
