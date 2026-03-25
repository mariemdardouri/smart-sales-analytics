import React, { useState } from "react";
import API from "../services/api";

function Prediction() {
  const [product, setProduct] = useState("");
  const [result, setResult] = useState([]);

  const predict = () => {
    API.get(`/forecast/product?name=${product}`)
      .then(res => setResult(res.data))
      .catch(err => console.error(err));
  };

  return (
    <div>
      <h2>Forecast Produit</h2>

      <input
        placeholder="Nom produit"
        value={product}
        onChange={(e) => setProduct(e.target.value)}
      />

      <button onClick={predict}>Predict</button>

      {result.map((r, i) => (
        <div key={i}>
          {r.ds} → {r.yhat}
        </div>
      ))}
    </div>
  );
}

export default Prediction;