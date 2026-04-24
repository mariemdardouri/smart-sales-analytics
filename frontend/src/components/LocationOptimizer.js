import React, { useState, useEffect } from "react";
import "./LocationOptimizer.css";

function LocationOptimizer() {
  const [categories, setCategories]         = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [brand, setBrand]                   = useState("");
  const [product, setProduct]               = useState("");
  const [topN, setTopN]                     = useState(5);
  const [result, setResult]                 = useState(null);
  const [metrics, setMetrics]               = useState(null);
  const [loading, setLoading]               = useState(false);
  const [showMetrics, setShowMetrics]       = useState(false);
  const [error, setError]                   = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/location/categories")
      .then(r => r.json()).then(setCategories)
      .catch(() => setError("Impossible de charger les catégories."));

    fetch("http://127.0.0.1:8000/location/metrics")
      .then(r => r.json()).then(setMetrics)
      .catch(() => {});
  }, []);

  const handlePredict = async () => {
    if (!selectedCategory) { alert("Veuillez sélectionner une catégorie."); return; }
    setLoading(true); setError(null); setResult(null);

    try {
      const res  = await fetch("http://127.0.0.1:8000/location/predict", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category:     selectedCategory,
          brand:        brand.trim()   || null,
          product_name: product.trim() || null,
          top_n:        topN,
        }),
      });
      const data = await res.json();
      if (!data.success) setError(data.error || "Erreur lors de la prédiction.");
      else {
        setResult(data);
        if (data.model_metrics) setMetrics(data.model_metrics);
      }
    } catch { setError("Erreur de connexion au serveur."); }
    finally  { setLoading(false); }
  };

  const fmt = (n) =>
    (n || n === 0)
      ? new Intl.NumberFormat("fr-TN", { style:"currency", currency:"TND", maximumFractionDigits:0 }).format(n)
      : "— DT";

  const scoreClass  = s => s >= 75 ? "high" : s >= 45 ? "medium" : "low";
  const r2Color     = r => r >= 0.85 ? "#28a745" : r >= 0.70 ? "#ffc107" : r >= 0.50 ? "#fd7e14" : "#dc3545";
  const gapClass    = g => g === undefined ? "" : g > 0.15 ? "gap-bad" : g > 0.05 ? "gap-warn" : "gap-good";

  return (
    <div className="location-optimizer">
      <div className="location-card">

        {/* En-tête */}
        <div className="loc-header">
          <h2>📍 Quelle région pour maximiser vos ventes ?</h2>
          <p className="subtitle">Sélectionnez une catégorie et affinez avec une marque ou un produit.</p>
        </div>

        {/* Formulaire */}
        <div className="loc-form">

          <div className="form-group">
            <label className="form-label">Catégorie <span className="required">*</span></label>
            <select className="loc-select" value={selectedCategory}
              onChange={e => setSelectedCategory(e.target.value)}>
              <option value="">— Choisir une catégorie —</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Marque <span className="optional">(optionnel)</span></label>
            <input className="loc-input" placeholder="Ex: DELICE, COCA…"
              value={brand} onChange={e => setBrand(e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label">Nom du produit <span className="optional">(optionnel)</span></label>
            <input className="loc-input" placeholder="Ex: Shampooing, Fromage râpé…"
              value={product} onChange={e => setProduct(e.target.value)} />
          </div>

          <div className="form-group form-group--small">
            <label className="form-label">Régions à afficher</label>
            <input type="number" className="loc-input loc-input--small"
              value={topN} min={1} max={20}
              onChange={e => setTopN(Math.max(1, parseInt(e.target.value) || 5))} />
          </div>

          <button className="loc-button" onClick={handlePredict}
            disabled={loading || !selectedCategory}>
            {loading ? "Analyse en cours…" : "🎯 Trouver les meilleures régions"}
          </button>
        </div>

        {error && <div className="loc-error">⚠️ {error}</div>}

        {/* Résultats */}
        {result && (
          <div className="loc-result">

            {result.note && <div className="loc-note">ℹ️ {result.note}</div>}

            {result.input?.filtre_applique && (
              <div className="loc-filter-tag">
                ✅ Filtré sur&nbsp;
                {result.input.marque   && <strong>{result.input.marque}</strong>}
                {result.input.marque && result.input.produit && " + "}
                {result.input.produit  && <strong>{result.input.produit}</strong>}
              </div>
            )}

            {/* Meilleure région */}
            <div className="best-region">
              <div className="best-label">🏆 Meilleure région estimée</div>
              <div className="best-name">{result.best_region}</div>
              <div className="best-ca">{fmt(result.best_ca)}</div>
              <div className="best-score">Score relatif : {result.best_score}%</div>
            </div>

            {/* Classement */}
            <div className="ranking">
              <h4>Classement des régions</h4>
              {result.top_regions.map((r, i) => (
                <div key={i} className="rank-item">
                  <span className="rank-num">{i + 1}</span>
                  <span className="rank-name">{r.region}</span>
                  <div className="rank-bar-wrap">
                    <div className="rank-bar" style={{ width: `${r.score}%` }} />
                  </div>
                  <span className="rank-ca">{fmt(r.ca_predit)}</span>
                  <span className={`rank-badge ${scoreClass(r.score)}`}>{r.confidence}</span>
                </div>
              ))}
            </div>

            {/* Toggle métriques */}
            <button className="metrics-toggle" onClick={() => setShowMetrics(v => !v)}>
              {showMetrics ? "▲ Masquer les métriques" : "▼ Voir les métriques du modèle"}
            </button>

            {showMetrics && metrics && (
              <div className="metrics-panel">
                <h4>Performance du modèle</h4>

                {/* R² TRAIN vs TEST */}
                <div className="r2-comparison">
                  <div className="r2-box">
                    <div className="r2-label">R² TRAIN</div>
                    <div className="r2-value" style={{ color: r2Color(metrics.r2_train) }}>
                      {metrics.r2_train ?? "—"}
                    </div>
                    <div className="r2-hint">données d'entraînement</div>
                  </div>

                  <div className="r2-arrow">→</div>

                  <div className="r2-box">
                    <div className="r2-label">R² TEST</div>
                    <div className="r2-value" style={{ color: r2Color(metrics.r2_test) }}>
                      {metrics.r2_test ?? "—"}
                    </div>
                    <div className="r2-hint">données inconnues</div>
                  </div>

                  <div className={`r2-gap-box ${gapClass(metrics.overfit_gap)}`}>
                    <div className="r2-label">ÉCART</div>
                    <div className="r2-value">
                      {metrics.overfit_gap !== undefined
                        ? metrics.overfit_gap.toFixed(3) : "—"}
                    </div>
                    <div className="r2-hint">train − test</div>
                  </div>
                </div>

                {metrics.overfit_status && (
                  <div className="overfit-status">{metrics.overfit_status}</div>
                )}

                {/* Autres métriques */}
                <div className="metrics-grid">
                  <div className="metric-box">
                    <div className="metric-value">
                      {metrics.mae
                        ? `${Math.round(metrics.mae).toLocaleString("fr-TN")} DT` : "—"}
                    </div>
                    <div className="metric-label">MAE</div>
                    <div className="metric-hint">Erreur absolue moyenne</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-value">{metrics.mape ? `${metrics.mape}%` : "—"}</div>
                    <div className="metric-label">MAPE</div>
                    <div className="metric-hint">Erreur % moyenne</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-value">{metrics.train_size ?? "—"}</div>
                    <div className="metric-label">Train</div>
                    <div className="metric-hint">échantillons</div>
                  </div>
                  <div className="metric-box">
                    <div className="metric-value">{metrics.test_size ?? "—"}</div>
                    <div className="metric-label">Test</div>
                    <div className="metric-hint">échantillons</div>
                  </div>
                </div>

                {metrics.interpretation && (
                  <div className="metrics-interpretation">{metrics.interpretation}</div>
                )}

                <div className="metrics-legend">
                  <strong>R² :</strong>
                  <span className="legend-item good">≥ 0.85 Excellent</span>
                  <span className="legend-item ok">≥ 0.70 Bon</span>
                  <span className="legend-item warn">≥ 0.50 Acceptable</span>
                  <span className="legend-item bad">&lt; 0.50 Faible</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default LocationOptimizer;