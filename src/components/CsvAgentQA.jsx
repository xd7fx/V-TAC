import React, { useState } from "react";

const CsvAgentQA = () => {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/ask-csv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setResponse(data.response || "❌ لم يتم الحصول على رد.");
    } catch (err) {
      setResponse("❌ خطأ أثناء التحليل.");
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="csv-agent-box" style={{ padding: "1rem", border: "1px solid #ccc", borderRadius: "10px" }}>
      <h3>🧠 اسأل عن ملف المباريات</h3>
      <input
        type="text"
        placeholder="مثلاً: كم مرة فاز ريال مدريد؟"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
      />
      <button onClick={handleAsk} disabled={loading} style={{ padding: "0.5rem 1rem" }}>
        {loading ? "⏳ جاري التحليل..." : "🔍 تحليل"}
      </button>
      {response && (
        <div style={{ marginTop: "1rem", background: "#f9f9f9", padding: "0.5rem", borderRadius: "5px" }}>
          <strong>🤖 الرد:</strong> {response}
        </div>
      )}
    </div>
  );
};

export default CsvAgentQA;
