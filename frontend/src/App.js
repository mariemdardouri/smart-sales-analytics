import React, { useState } from "react";
import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import Dashboard from "./components/Dashboard";
import Chatbot from "./components/Chatbot";
import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");

  return (
    <div className="app-container">
      <Chatbot />
      {/* Sidebar */}
      <aside className="sidebar">
        <h2 className="logo">Smart Sales Analytics</h2>

        <button onClick={() => setPage("dashboard")} className={page === "dashboard" ? "active" : ""}>
          📊 Dashboard
        </button>

        <button onClick={() => setPage("basket")} className={page === "basket" ? "active" : ""}>
          🛒 Basket
        </button>

        <button onClick={() => setPage("prediction")} className={page === "prediction" ? "active" : ""}>
          📈 Prediction
        </button>
      </aside>

      {/* Main */}
      <div className="main">
        
        {/* Topbar */}
        <header className="topbar">
          <h1>{page.toUpperCase()}</h1>
        </header>

        {/* Content */}
        <div className="content">
          {page === "dashboard" && <Dashboard />}
          {page === "basket" && <BasketAnalysis />}
          {page === "prediction" && <Prediction />}
        </div>

      </div>
    </div>
  );
}

export default App;
