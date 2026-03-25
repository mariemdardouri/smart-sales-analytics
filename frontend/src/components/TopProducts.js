import React, { useEffect, useState } from "react";
import API from "../services/api";

function TopProducts() {
  const [data, setData] = useState([]);

  useEffect(() => {
    API.get("/products/top")
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>🔥 Top Produits</h2>
      {data.map((p, i) => (
        <div key={i}>
          {p.nom_produit} → {p.quantité_achetée}
        </div>
      ))}
    </div>
  );
}

export default TopProducts;