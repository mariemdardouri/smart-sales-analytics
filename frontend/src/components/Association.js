import React, { useEffect, useState } from "react";
import API from "../services/api";

function Association() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    API.get("/association")
      .then(res => {
        const result = res.data;
        console.log("Association API response:", result); // remove once working

        if (Array.isArray(result)) {
          setData(result);
        } else if (Array.isArray(result?.rules)) {
          setData(result.rules);
        } else if (Array.isArray(result?.data)) {
          setData(result.data);
        } else {
          setData([]);
        }
      })
      .catch(err => {
        console.error(err);
        setError("Impossible de charger les associations.");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="card">Chargement...</div>;
  if (error) return <div className="card" style={{ color: "red" }}>{error}</div>;
  if (data.length === 0) return <div className="card">Aucune association trouvée.</div>;

  return (
    <div className="card">
      <h2>🛒 Associations de produits</h2>
      {data.map((rule, i) => (
        <div key={i}>
          {Array.from(rule.antecedents).join(", ")} → {Array.from(rule.consequents).join(", ")}
        </div>
      ))}
    </div>
  );
}

export default Association;