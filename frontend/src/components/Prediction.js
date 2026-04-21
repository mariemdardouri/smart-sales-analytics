import React, { useState } from "react";
import API from "../services/api";
import "./Prediction.css";

function Prediction() {
  const [product, setProduct] = useState("");
  const [result, setResult] = useState([]);
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    try {
      const res = await API.get(`/forecast/product?name=${product}`);
      if (Array.isArray(res.data)) {
        setResult(res.data);
      } else {
        alert(res.data.error || "Error");
        setResult([]);
      }
    } catch (err) {
      console.error(err);
      alert("Error fetching prediction");
    }
    setLoading(false);
  };

  return (
    <div className="prediction-container">
      <h2 className="prediction-title">📊 Forecast Produit</h2>

      <div className="prediction-input-container">
        <input
          className="prediction-input"
          placeholder="Nom produit..."
          value={product}
          onChange={(e) => setProduct(e.target.value)}
        />

        <button className="prediction-button" onClick={predict}>
          Predict
        </button>
      </div>

      {loading && <p className="loading">Loading...</p>}

      <div className="prediction-results">
        {result.map((r, i) => (
          <div key={i} className="prediction-card">
            <p><strong>Date:</strong> {r.ds}</p>
            <p>
              <strong>Probability:</strong>{" "}
              <span className={getClass(r.probability)}>
                {r.probability.toFixed(1)}%
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

const getClass = (value) => {
  if (value > 70) return "high";
  if (value > 40) return "medium";
  return "low";
};

export default Prediction;