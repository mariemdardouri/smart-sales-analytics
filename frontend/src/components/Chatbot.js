import React, { useState, useRef, useEffect } from "react";
import { sendQuestion } from "./ChatService";
import "./Chatbot.css";

function Chatbot() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "🤖 Bonjour ! Pose-moi une question sur tes ventes 📊",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    }
  ]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ SEND MESSAGE
  const handleSend = async (customText = null) => {
    const text = customText || question;

    if (!text.trim() || loading) return;

    const userMsg = {
      role: "user",
      text: text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages(prev => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await sendQuestion(text);

      const botMsg = {
        role: "bot",
        text: res,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };

      setMessages(prev => [...prev, botMsg]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: "bot",
          text: "❌ Error connecting to server",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    }

    setLoading(false);
  };

  // ✅ SUGGESTIONS
  const suggestions = [
    "Top 5 produits",
    "Produits achetés ensemble",
    "Compare Tunis et Sfax",
    "Top catégorie boissons"
  ];

  // ✅ VOICE
  const handleVoice = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "fr-FR";

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      handleSend(text); // 🔥 auto send
    };

    recognition.start();
  };

  return (
    <>
      {/* 🔵 FLOATING CIRCLE */}
      <div className="chatbot-circle" onClick={() => setOpen(!open)}>
        💬
      </div>

      {/* 💬 CHAT WINDOW */}
      {open && (
        <div className="chatbot-box">

          {/* HEADER */}
          <div className="chatbot-header">
            <span>🤖 Assistant IA</span>
            <button onClick={() => setOpen(false)}>✖</button>
          </div>

          {/* MESSAGES */}
          <div className="chatbot-messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div>
                  {m.text}
                  <div className="msg-time">{m.time}</div>
                </div>
              </div>
            ))}

            {loading && <div className="msg bot">Typing...</div>}
            <div ref={messagesEndRef}></div>
          </div>

          {/* SUGGESTIONS */}
          <div className="suggestions">
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => handleSend(s)}>
                {s}
              </button>
            ))}
          </div>

          {/* INPUT */}
          <div className="chatbot-input">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Pose ta question..."
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button onClick={handleVoice}>🎤</button>
            <button onClick={() => handleSend()}>Send</button>
          </div>

        </div>
      )}
    </>
  );
}

export default Chatbot;