import React, { useEffect, useState } from "react";
import API from "./services/api";

function Dashboard() {
  const [sales, setSales] = useState(0);

  useEffect(() => {
    API.get("/sales/total")
      .then(res => {
        setSales(res.data.total_sales);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h1>Smart Sales Analytics Dashboard</h1>
      <h2>Total Sales: {sales}</h2>
    </div>
  );
}

export default Dashboard;