// src/components/HomePage.js
import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", padding: "50px" }}>
      <h1>Bienvenue sur Smart Sales Analytics</h1>
      <p>Découvrez les modèles de prédiction et les analyses de vos ventes.</p>
      <button
        style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}
        onClick={() => navigate("/app")}
      >
        Commencer
      </button>
    </div>
  );
}

export default HomePage;