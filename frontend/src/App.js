import React, { useState } from "react";
import Dashboard from "./Dashboard";
import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import "./App.css"; // Import the new CSS file

function App() {
  const [page, setPage] = useState("home");
  const [chatOpen, setChatOpen] = useState(false);
  return (
    <div className="App">
      <header className="app-header">
        <nav className="nav-bar">
          <button
            className={`nav-button ${page === "home" ? "active" : ""}`}
            onClick={() => setPage("home")}
          >
            Home
          </button>
          <button
            className={`nav-button ${page === "dashboard" ? "active" : ""}`}
            onClick={() => setPage("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={`nav-button ${page === "basket" ? "active" : ""}`}
            onClick={() => setPage("basket")}
          >
            Basket Analysis
          </button>
          <button
            className={`nav-button ${page === "prediction" ? "active" : ""}`}
            onClick={() => setPage("prediction")}
          >
            Prediction
          </button>
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
            <button className="cta-button" onClick={() => setPage("dashboard")}>
              Start the App
            </button>
          </div>
        )}

        {page === "dashboard" && <Dashboard />}
        {page === "basket" && <BasketAnalysis />}
        {page === "prediction" && <Prediction />}
      </main>
      {/* Chatbot Bubble */}
<div 
  className="chatbot-bubble"
  onClick={() => setChatOpen(!chatOpen)}
>
  💬
  <span className="chatbot-tooltip">Chatbot</span>
</div>

{/* Chatbot Window */}
{chatOpen && (
  <div className="chatbot-window">
    <div className="chatbot-header">
      <span>Chatbot</span>
      <button onClick={() => setChatOpen(false)}>✖</button>
    </div>
    <div className="chatbot-body">
      <p>Bonjour 👋 Pose ta question</p>
    </div>
  </div>
)}
    </div>
  );
}

export default App;