import React from "react";
import TopProducts from "./TopProducts";
import ClientProducts from "./ClientProducts";
import Association from "./Association";
import Forecast from "./Forecast";

function Dashboard() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>📊 Smart Sales Dashboard</h1>

      <TopProducts />
      <ClientProducts />
      <Association />
      <Forecast />
    </div>
  );
}

export default Dashboard;