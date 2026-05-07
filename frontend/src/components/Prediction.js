import React, { useState, useEffect, useRef } from "react";
import API from "../services/api";
import { Line } from "react-chartjs-2";
import "chart.js/auto";
import "./Prediction.css";

const SUGGESTIONS = [
  "shampooing", "masque capillaire", "après shampooing",
  "déodorant homme", "boisson gazeuse", "gel douche",
  "crème visage", "dentifrice", "savon", "lait corporel"
];

function Prediction() {
  const [product, setProduct] = useState("");
  const [result, setResult] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState("");
  const [filtered, setFiltered] = useState([]);
  const [showSugg, setShowSugg] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef();


  const [months, setMonths] = useState(3);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    if (product.length < 2) { setFiltered([]); return; }
    setFiltered(
      SUGGESTIONS.filter(s => s.toLowerCase().includes(product.toLowerCase())).slice(0, 5)
    );
  }, [product]);

  const predict = async (name = product) => {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    setResult([]);
    setShowSugg(false);
    try {
      const res = await API.get(
        `/forecast/product?name=${encodeURIComponent(name)}&periods=${months}`
      );

      const data = res.data;
      
      if (data?.forecast && Array.isArray(data.forecast)) {
        setResult(data.forecast);
        setSearched(name);
        setMetrics(data.metrics);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError("Aucun résultat trouvé pour ce produit.");
      }
    } catch {
      setError("Impossible de contacter le serveur.");
    }
    
    setLoading(false);
  };

  const handleKey = (e) => {
    if (e.key === "Enter") predict();
  };

  const forecast = result || [];
  const maxY = Math.max(...forecast.map(r => r.yhat || 0), 1);

  const chartData = {
    labels: result.map(r => r.ds),
    datasets: [
      {
        label: "Prévision",
        data: result.map(r => r.yhat),
        borderColor: "#f59e0b",
        backgroundColor: "rgba(245,158,11,0.10)",
        fill: true,
        borderDash: [6, 3],
        pointRadius: 3,
        tension: 0.35,
      },
    ]
  };
  const chartOpts = {
    responsive: true,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#94a3b8",
          font: { family: "'DM Sans', sans-serif", size: 12 },
          usePointStyle: true,
          filter: item => !item.text.includes("Intervalle"),
        }
      },
      tooltip: {
        backgroundColor: "#1e293b",
        titleColor: "#f8fafc",
        bodyColor: "#94a3b8",
        borderColor: "#334155",
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: ctx => {
            const v = ctx.raw;
            if (v === null) return null;
            return ` ${ctx.dataset.label}: ${v >= 1000 ? (v/1000).toFixed(1)+"K" : v?.toFixed(1)}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: "rgba(51,65,85,0.5)" },
        ticks: { color: "#64748b", font: { size: 11 } }
      },
      y: {
        grid: { color: "rgba(51,65,85,0.5)" },
        ticks: { color: "#64748b", font: { size: 11 } }
      }
    }
  };

  const getLevel = (prob) => {
    if (prob > 70) return { label: "Forte demande", color: "#10b981", bg: "rgba(16,185,129,0.12)" };
    if (prob > 40) return { label: "Demande modérée", color: "#f59e0b", bg: "rgba(245,158,11,0.12)" };
    return { label: "Faible demande", color: "#ef4444", bg: "rgba(239,68,68,0.12)" };
  };

  return (
    <div className="pred-root">

      {/* ── HEADER ── */}
      <div className="pred-header">
        <div className="pred-header-icon">📈</div>
        <div>
          <h1 className="pred-title">Prédiction Produit</h1>
          <p className="pred-subtitle">
            Prévision des ventes par produit sur {months} mois
          </p>
        </div>
      </div>

      {/* ── SEARCH ── */}
      <div className="pred-search-wrap">
        <div className="pred-search-box">
          <span className="pred-search-icon">🔍</span>
          <input
            ref={inputRef}
            className="pred-input"
            placeholder="Entrez un nom de produit..."
            value={product}
            onChange={e => { setProduct(e.target.value); setShowSugg(true); }}
            onKeyDown={handleKey}
            onFocus={() => setShowSugg(true)}
            onBlur={() => setTimeout(() => setShowSugg(false), 150)}
            autoComplete="off"
          />
          <button
            className="pred-btn"
            onClick={() => predict()}
            disabled={loading || !product.trim()}
          >
            {loading ? "Analyse..." : "Analyser"}
          </button>
        </div>

       <div className="pred-controls">
          <span>Durée :</span>

          {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
            <button
              key={m}
              className={months === m ? "active" : ""}
              onClick={() => setMonths(m)}
            >
              {m} mois
            </button>
          ))}
        </div>
        {/* suggestions dropdown */}
        {showSugg && filtered.length > 0 && (
          <div className="pred-suggestions">
            {filtered.map((s, i) => (
              <div
                key={i}
                className="pred-suggestion-item"
                onMouseDown={() => { setProduct(s); predict(s); }}
              >
                <span className="sugg-icon">📦</span> {s}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── ERROR ── */}
      {error && (
        <div className="pred-error">
          ⚠️ {error}
        </div>
      )}

      {/* ── LOADING ── */}
      {loading && (
        <div className="pred-loading">
          <div className="pred-loading-bar" />
          <p>Calcul de la prévision en cours...</p>
        </div>
      )}

      {/* ── RESULTS ── */}
      {result.length > 0 && !loading && (
        <div className="pred-results">

          {/* product badge */}
          <div className="pred-product-badge">
            <span className="badge-dot" />
            Résultats pour : <strong>{searched}</strong>
          </div>

          {/* forecast cards */}
          <div className="pred-cards">
            {forecast.map((r, i) => {
              const prob = maxY ? ((r.yhat || 0) / maxY) * 100 : 0;
              const level = getLevel(prob);
              return (
                <div className="pred-card" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
                  <div className="pred-card-month">
                    {typeof r.ds === "string" ? r.ds : new Date(r.ds).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })}
                  </div>
                  <div className="pred-card-prob" style={{ color: level.color }}>
                    {prob.toFixed(1)}%
                  </div>
                  <div className="pred-card-bar-track">
                    <div
                      className="pred-card-bar-fill"
                      style={{ width: `${Math.min(prob, 100)}%`, background: level.color }}
                    />
                  </div>
                  <div className="pred-card-label" style={{ color: level.color, background: level.bg }}>
                    {level.label}
                  </div>
                  {r.yhat && (
                    <div className="pred-card-value">
                      CA prévu: <strong>
                        {r.yhat >= 1_000_000
                          ? (r.yhat / 1_000_000).toFixed(2) + "M"
                          : r.yhat >= 1000
                          ? (r.yhat / 1000).toFixed(1) + "K"
                          : r.yhat.toFixed(0)}
                      </strong>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* chart */}
          <div className="pred-chart-card">
            <h3 className="pred-chart-title">Tendance des ventes</h3>
            <div className="pred-chart-inner">
              <Line data={chartData} options={chartOpts} />
            </div>
          </div>

        </div>
      )}

      {/* ── EMPTY STATE ── */}
      {result.length === 0 && !loading && !error && (
        <div className="pred-empty">
          <div className="pred-empty-icon">📊</div>
          <p>Recherchez un produit pour voir sa prévision de ventes</p>
          <div className="pred-hints">
            {["shampooing", "masque capillaire", "gel douche"].map(s => (
              <button key={s} className="pred-hint-chip" onClick={() => { setProduct(s); predict(s); }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
      {metrics && (
        <div className="pred-product-badge">
          MAE: {metrics.MAE?.toFixed(3)} |
          RMSE: {metrics.RMSE?.toFixed(3)} |
          R²: {metrics.R2?.toFixed(2)}
        </div>
      )}

    </div>
  );
}

export default Prediction;