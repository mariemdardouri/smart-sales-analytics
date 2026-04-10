import React, { useState, useRef, useEffect } from "react";
import Dashboard from "./Dashboard";
import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import "./App.css";
import { sendQuestion } from "./components/ChatService";

function App() {
  const [page, setPage] = useState("home");
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Nouveaux states pour l'historique des messages
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: 'Bonjour ! Je suis votre assistant IA. Comment puis-je vous aider avec l\'analyse de ventes ?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  
  const messagesEndRef = useRef(null);

  // Scroll automatique vers le bas quand un nouveau message arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!question.trim() || loading) return;

    // Ajouter le message utilisateur
    const userMessage = {
      role: 'user',
      content: question,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMessage]);
    
    const currentQuestion = question;
    setQuestion("");
    setLoading(true);

    try {
      const res = await sendQuestion(currentQuestion);
      
      // Ajouter la réponse du bot
      const botMessage = {
        role: 'bot',
        content: res || "Désolé, je n'ai pas pu traiter votre demande.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error:', err);
      const errorMessage = {
        role: 'bot',
        content: "Erreur lors de l'envoi au backend. Veuillez réessayer.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <nav className="nav-bar">
          <button className={`nav-button ${page === "home" ? "active" : ""}`} onClick={() => setPage("home")}>Home</button>
          <button className={`nav-button ${page === "dashboard" ? "active" : ""}`} onClick={() => setPage("dashboard")}>Dashboard</button>
          <button className={`nav-button ${page === "basket" ? "active" : ""}`} onClick={() => setPage("basket")}>Basket Analysis</button>
          <button className={`nav-button ${page === "prediction" ? "active" : ""}`} onClick={() => setPage("prediction")}>Prediction</button>
        </nav>
      </header>

      <main className="app-main">
        {page === "home" && (
          <div className="hero-section">
            <h1>Welcome to Smart Sales Analytics</h1>
            <p className="hero-description">
              This application allows you to analyze sales, predict purchases,
              and discover which products are often bought together.
            </p>
            <button className="cta-button" onClick={() => setPage("dashboard")}>Start the App</button>
          </div>
        )}
        {page === "dashboard" && <Dashboard />}
        {page === "basket" && <BasketAnalysis />}
        {page === "prediction" && <Prediction />}
      </main>

      {/* Chatbot Bubble */}
      <div className="chatbot-bubble" onClick={() => setChatOpen(!chatOpen)}>
        <span className="chatbot-icon">💬</span>
        {!chatOpen && <span className="chatbot-tooltip">Assistant IA</span>}
        {!chatOpen && <span className="notification-dot"></span>}
      </div>

      {/* Chatbot Window */}
      {chatOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <span className="chatbot-header-icon">🤖</span>
              <div>
                <h3>Assistant IA</h3>
                <p>En ligne • Analyse de ventes</p>
              </div>
            </div>
            <button className="chatbot-close" onClick={() => setChatOpen(false)}>✖</button>
          </div>
          
          <div className="chatbot-messages" ref={messagesEndRef}>
            {messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  <div className="message-time">{msg.time}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message bot-message">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chatbot-input-area">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Pose ta question..."
              rows="1"
            />
            <button onClick={handleSend} disabled={loading || !question.trim()}>
              {loading ? <span className="spinner"></span> : 'Envoyer'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;