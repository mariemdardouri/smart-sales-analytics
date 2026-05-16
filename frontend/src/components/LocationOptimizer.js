import React, { useState, useEffect } from "react";
import "./LocationOptimizer.css";

// Icônes SVG - Version professionnelle
const CategoryIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 7h-4.18A3 3 0 0 0 16 5.18V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v1.18A3 3 0 0 0 8.18 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/>
    <line x1="12" y1="11" x2="12" y2="17"/>
    <line x1="9" y1="14" x2="15" y2="14"/>
  </svg>
);

const BrandIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8.5L4 6.5V20a2 2 0 0 0 2 2Z"/>
    <polyline points="14 2 14 6 18 6"/>
  </svg>
);

const ProductIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="2" width="6" height="6" rx="1"/>
    <rect x="4" y="10" width="16" height="12" rx="2"/>
    <line x1="9" y1="16" x2="15" y2="16"/>
    <line x1="12" y1="13" x2="12" y2="19"/>
  </svg>
);

const LocationIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
);

const TrophyIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
    <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
    <path d="M4 22h16"/>
    <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
    <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
    <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>
  </svg>
);

const ChartIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    <polyline points="3.29 7 12 12 20.71 7"/>
    <line x1="12" y1="22" x2="12" y2="12"/>
  </svg>
);

const TrendingUpIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
    <polyline points="17 6 23 6 23 12"/>
  </svg>
);

function LocationOptimizer() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [product, setProduct] = useState("");
  const [topN, setTopN] = useState(5);
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showMetrics, setShowMetrics] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/location/categories")
      .then(r => r.json())
      .then(data => {
        console.log("Catégories chargées:", data);
        setCategories(data || []);
      })
      .catch(() => setError("Impossible de charger les catégories."));

    fetch("http://127.0.0.1:8000/location/metrics")
      .then(r => r.json())
      .then(data => setMetrics(data))
      .catch(() => {});
  }, []);

  const handlePredict = async () => {
    if (!selectedCategory) {
      alert("Veuillez sélectionner une catégorie.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/location/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: selectedCategory,
          brand: brand.trim() || null,
          product_name: product.trim() || null,
          top_n: topN,
        }),
      });
      const data = await res.json();
      if (!data.success) setError(data.error || "Erreur lors de la prédiction.");
      else {
        setResult(data);
        if (data.model_metrics) setMetrics(data.model_metrics);
      }
    } catch {
      setError("Erreur de connexion au serveur.");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (n) =>
    (n || n === 0)
      ? new Intl.NumberFormat("fr-TN", { style: "currency", currency: "TND", maximumFractionDigits: 0 }).format(n)
      : "— DT";

  const scoreClass = s => s >= 75 ? "high" : s >= 45 ? "medium" : "low";
  const r2Color = r => r >= 0.85 ? "#10b981" : r >= 0.70 ? "#f59e0b" : r >= 0.50 ? "#f97316" : "#ef4444";
  const gapClass = g => g === undefined ? "" : g > 0.15 ? "gap-bad" : g > 0.05 ? "gap-warn" : "gap-good";

  return (
    <div className="loc-container">
      <div className="loc-card">

        {/* Header */}
        <div className="loc-header">
          <div className="loc-header-icon">
            <LocationIcon />
          </div>
          <h1>Analyse de performance régionale</h1>
          <p className="loc-subtitle">Identifiez les zones géographiques les plus rentables pour votre offre</p>
        </div>

        {/* Formulaire */}
        <div className="loc-form">
          <div className="form-row">
            <div className="form-field">
              <label className="form-field-label">
                <CategoryIcon />
                <span>Catégorie</span>
              </label>
              <select
                className="loc-select"
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
              >
                <option value="">Sélectionner une catégorie</option>
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label className="form-field-label">
                <BrandIcon />
                <span>Marque</span>
              </label>
              <input
                className="loc-input"
                placeholder="Optionnel"
                value={brand}
                onChange={e => setBrand(e.target.value)}
              />
            </div>

            <div className="form-field">
              <label className="form-field-label">
                <ProductIcon />
                <span>Produit spécifique</span>
              </label>
              <input
                className="loc-input"
                placeholder="Optionnel"
                value={product}
                onChange={e => setProduct(e.target.value)}
              />
            </div>

            <div className="form-field form-field-small">
              <label className="form-field-label">
                <ChartIcon />
                <span>Nombre de régions</span>
              </label>
              <input
                type="number"
                className="loc-input"
                value={topN}
                min={1}
                max={20}
                onChange={e => setTopN(Math.max(1, parseInt(e.target.value) || 5))}
              />
            </div>
          </div>

          <button className="loc-button" onClick={handlePredict} disabled={loading || !selectedCategory}>
            {loading ? (
              <>
                <span className="spinner-small"></span>
                Analyse en cours...
              </>
            ) : (
              <>
                <TrendingUpIcon />
                Analyser les performances
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="loc-error">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Résultats */}
        {result && (
          <div className="loc-results">
            {result.note && (
              <div className="info-banner">
                <span>ℹ️</span> {result.note}
              </div>
            )}

            {/* Meilleure région */}
            <div className="best-region-card">
              <div className="best-region-icon">
                <TrophyIcon />
              </div>
              <div className="best-region-content">
                <div className="best-region-label">Région la plus performante</div>
                <div className="best-region-name">{result.best_region}</div>
                <div className="best-region-stats">
                  <span className="best-region-ca">{formatCurrency(result.best_ca)}</span>
                  <span className="best-region-score">Score {result.best_score}%</span>
                </div>
              </div>
            </div>

            {/* Classement des régions */}
            <div className="ranking-section">
              <h3 className="ranking-title">Classement des régions</h3>
              <div className="ranking-list">
                {result.top_regions.map((r, i) => (
                  <div key={i} className="ranking-item">
                    <div className="ranking-position">{i + 1}</div>
                    <div className="ranking-name">{r.region}</div>
                    <div className="ranking-bar-container">
                      <div className="ranking-bar" style={{ width: `${r.score}%` }} />
                    </div>
                    <div className="ranking-ca">{formatCurrency(r.ca_predit)}</div>
                    <div className={`ranking-badge ${scoreClass(r.score)}`}>{r.confidence}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Toggle métriques */}
            <button className="metrics-toggle" onClick={() => setShowMetrics(v => !v)}>
              {showMetrics ? "▲ Masquer les métriques" : "▼ Voir les métriques du modèle"}
            </button>

            {/* Métriques du modèle */}
            {showMetrics && metrics && (
              <div className="metrics-panel">
                <h3 className="metrics-title">Performance du modèle prédictif</h3>

                <div className="r2-comparison">
                  <div className="r2-card">
                    <div className="r2-label">Entraînement</div>
                    <div className="r2-value" style={{ color: r2Color(metrics.r2_train) }}>
                      {(metrics.r2_train * 100).toFixed(1)}%
                    </div>
                    <div className="r2-sub">R² sur données d'entraînement</div>
                  </div>

                  <div className="r2-arrow">→</div>

                  <div className="r2-card">
                    <div className="r2-label">Validation</div>
                    <div className="r2-value" style={{ color: r2Color(metrics.r2_test) }}>
                      {(metrics.r2_test * 100).toFixed(1)}%
                    </div>
                    <div className="r2-sub">R² sur données de test</div>
                  </div>

                  <div className={`r2-gap ${gapClass(metrics.overfit_gap)}`}>
                    <div className="r2-label">Écart</div>
                    <div className="r2-value">
                      {metrics.overfit_gap !== undefined ? (metrics.overfit_gap * 100).toFixed(1) : "—"}%
                    </div>
                    <div className="r2-sub">Train - Test</div>
                  </div>
                </div>

                {metrics.overfit_status && (
                  <div className="overfit-message">{metrics.overfit_status}</div>
                )}

                <div className="metrics-grid">
                  <div className="metric-item">
                    <div className="metric-main">{formatCurrency(metrics.mae)}</div>
                    <div className="metric-label">Erreur absolue moyenne</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-main">{metrics.mape ? `${metrics.mape}%` : "—"}</div>
                    <div className="metric-label">Erreur relative moyenne</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-main">{metrics.train_size ?? "—"}</div>
                    <div className="metric-label">Échantillons entraînement</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-main">{metrics.test_size ?? "—"}</div>
                    <div className="metric-label">Échantillons validation</div>
                  </div>
                </div>

                {metrics.interpretation && (
                  <div className="interpretation-box">{metrics.interpretation}</div>
                )}

                <div className="r2-legend">
                  <span className="legend-dot excellent"></span>
                  <span>≥ 85%</span>
                  <span className="legend-dot good"></span>
                  <span>≥ 70%</span>
                  <span className="legend-dot fair"></span>
                  <span>≥ 50%</span>
                  <span className="legend-dot poor"></span>
                  <span>&lt; 50%</span>
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