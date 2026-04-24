import React, { useState } from "react";
import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import SalesPrediction from "./components/SalesPrediction";
import LocationOptimizer from "./components/LocationOptimizer";
import Dashboard from "./components/Dashboard";
import Chatbot from "./components/Chatbot";
import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");

  return (
    <div className="app-container">
      <Chatbot />
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
        <button onClick={() => setPage("location")} className={page === "location" ? "active" : ""}>
          📍 Où vendre ?
        </button>
      </aside>

      <div className="main">
        <header className="topbar">
          <h1>
            {page === "dashboard" && "DASHBOARD"}
            {page === "basket" && "ANALYSE DE PANIER"}
            {page === "prediction" && "PRÉDICTION - PRODUITS ASSOCIÉS"}
            {page === "sales" && "PRÉDICTION - CHIFFRE D'AFFAIRES"}
            {page === "location" && "OÙ VENDRE - RÉGIONS PERFORMANTES"}
          </h1>
        </header>
        <div className="content">
          {page === "dashboard" && <Dashboard />}
          {page === "basket" && <BasketAnalysis />}
          {page === "prediction" && <Prediction />}
          {page === "sales" && <SalesPrediction />}
          {page === "location" && <LocationOptimizer />}
        </div>
      </div>
    </div>
  );
}

export default App;