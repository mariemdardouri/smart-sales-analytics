import React, { useState } from "react";
import API from "../services/api";

function ClientProducts() {
  const [client, setClient] = useState("");
  const [data, setData] = useState([]);

  const fetchData = () => {
    API.get(`/products/client?client_id=${client}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  };

  return (
    <div>
      <h2>👤 Produits d’un client</h2>

      <input
        placeholder="Client ID"
        value={client}
        onChange={(e) => setClient(e.target.value)}
      />

      <button onClick={fetchData}>Search</button>

      {data.map((p, i) => (
        <div key={i}>{p}</div>
      ))}
    </div>
  );
}

export default ClientProducts;