import React, { useEffect, useState } from "react";
import API from "../services/api";

function Association() {
  const [data, setData] = useState([]);

  useEffect(() => {
    API.get("/association")
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>🛒 Associations de produits</h2>

      {data.map((rule, i) => (
        <div key={i}>
          {rule.antecedents} → {rule.consequents}
        </div>
      ))}
    </div>
  );
}

export default Association;