import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";
import API from "../services/api";

function SalesChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    API.get("/forecast")
      .then(res => {
        // adapt to your backend format
        const formatted = res.data.map(item => ({
          date: item.ds,
          sales: item.yhat
        }));
        setData(formatted);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="card">
      <h2>📈 Sales Forecast</h2>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#e5e7eb" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SalesChart;