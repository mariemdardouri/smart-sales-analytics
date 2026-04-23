import React, { useState } from "react";
import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import SalesPrediction from "./components/SalesPrediction"; // Nouveau composant
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
          📈 Prediction 1
        </button>

        <button onClick={() => setPage("sales")} className={page === "sales" ? "active" : ""}>
          💰 Prediction 2 - Ventes
        </button>
      </aside>

      {/* Main */}
      <div className="main">
        
        {/* Topbar */}
        <header className="topbar">
          <h1>
            {page === "dashboard" && "DASHBOARD"}
            {page === "basket" && "ANALYSE DE PANIER"}
            {page === "prediction" && "PRÉDICTION 1 - COMPORTEMENT"}
            {page === "sales" && "PRÉDICTION 2 - CHIFFRE D'AFFAIRES"}
          </h1>
        </header>

        {/* Content */}
        <div className="content">
          {page === "dashboard" && <Dashboard />}
          {page === "basket" && <BasketAnalysis />}
          {page === "prediction" && <Prediction />}
          {page === "sales" && <SalesPrediction />}
        </div>

      </div>
    </div>
  );
}

export default App;