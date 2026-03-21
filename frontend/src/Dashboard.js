import React, { useEffect, useState } from "react";
import API from "./services/api";

function Dashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    API.get("/basket")
      .then(res => {
        setData(res.data);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h1>Smart Sales Analytics Dashboard</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default Dashboard;