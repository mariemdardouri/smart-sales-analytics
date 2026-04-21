import React, { useEffect, useState } from "react";
import API from "../services/api";

function TopProducts() {
  const [data, setData] = useState([]);

  useEffect(() => {
    API.get("/products/top")
      .then(res => {
        console.log(res.data); // 👈 DEBUG
        setData(res.data);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="card">
      <h2>🔥 Top Produits</h2>

      {Array.isArray(data) ? (
        data.map((p, i) => (
          <div key={i}>
            {p.nom_produit} — <strong>{p.quantité_achetée}</strong>
          </div>
        ))
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default TopProducts;