import React, { useState, useEffect } from "react";

const ChatBot = ({ inputOverride, onBotReply }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // 🔽 Send a message to the LLM, and if it's from voice input, trigger avatar response
  const handleSend = async (text, fromVoice = false) => {
    const userInput = text || input;
    if (!userInput.trim()) return;

    setMessages((prev) => [...prev, { from: "user", text: userInput }]);

    try {
      // 1️⃣ Send to LLM model (e.g. Ollama, Mistral)
      const res = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput }),
      });

      const data = await res.json();
      const reply = data.reply || "⚠️ No response.";
      setMessages((prev) => [...prev, { from: "bot", text: reply }]);

      // ✅ If input is from voice, generate TTS and lipsync
      if (fromVoice && onBotReply) {
        const res2 = await fetch("http://localhost:5000/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: reply }),
        });

        const ttsData = await res2.json();
        if (!ttsData.filename) throw new Error("❌ Failed to generate TTS");

        await fetch("http://localhost:5000/api/lipsync", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: ttsData.filename }),
        });

        const scriptName = ttsData.filename.replace(".wav", "");
        onBotReply(scriptName);
      }

    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [...prev, {
        from: "bot",
        text: "⚠️ Server error."
      }]);
    }

    if (!text) setInput("");
  };

  // 📢 Triggered only when input is from voice
  useEffect(() => {
    if (inputOverride) {
      handleSend(inputOverride, true);
    }
  }, [inputOverride]);

  return (
    <div className="chat-box">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.from}`}>
            <strong>{msg.from === "user" ? "You: " : "Assistant: "}</strong> {msg.text}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={() => handleSend()}>Send</button>
      </div>
    </div>
  );
};

export default ChatBot;
