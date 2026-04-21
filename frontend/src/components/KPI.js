import React from "react";

function KPI({ title, value }) {
  return (
    <div className="kpi-card">
      <h4>{title}</h4>
      <p>{value}</p>
    </div>
  );
}

export default KPI;