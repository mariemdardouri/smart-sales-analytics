import React, { useState } from "react";
import API from "../services/api";

function Prediction() {
  const [qty, setQty] = useState("");
  const [price, setPrice] = useState("");
  const [result, setResult] = useState(null);

  const predict = () => {
    API.get(`/predict-customer?total=${price}&qty=${qty}`) // ⚠ route et params corrigés
      .then(res => {
        setResult(res.data.prediction);
      })
      .catch(err => console.error(err));
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Sales Prediction</h1>
      <input
        placeholder="Quantity"
        value={qty}
        onChange={e => setQty(e.target.value)}
      />
      <input
        placeholder="Total Price"
        value={price}
        onChange={e => setPrice(e.target.value)}
      />
      <button onClick={predict}>Predict</button>
      {result !== null && <h2>Prediction: {result}</h2>}
    </div>
  );
}

export default Prediction;