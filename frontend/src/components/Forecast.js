import React, { useState } from "react";
import API from "../services/api";

function Forecast() {
  const [product, setProduct] = useState("");
  const [data, setData] = useState([]);


    const fetchForecast = () => {
    if (!product) {
        alert("Enter product name");
        return;
    }

    API.get(`/forecast/product?name=${product}`)
        .then(res => setData(res.data))
        .catch(err => console.error(err));
    };

  return (
    <div>
      <h2>📈 Forecast Produit</h2>

      <input
        placeholder="Nom produit"
        value={product}
        onChange={(e) => setProduct(e.target.value)}
      />

      <button onClick={fetchForecast}>Predict</button>

      {data.map((f, i) => (
        <div key={i}>
          {f.ds} → {f.yhat}
        </div>
      ))}
    </div>
  );
}

export default Forecast;