import React, { useState, useEffect } from "react";
import "./SalesPrediction.css";

// Icônes SVG professionnelles
const SalesIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const CategoryCheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const LocationPinIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
);

const CalendarIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
    <line x1="3" y1="10" x2="21" y2="10"/>
    <line x1="8" y1="2" x2="8" y2="6"/>
    <line x1="16" y1="2" x2="16" y2="6"/>
  </svg>
);

const ChartBarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 20V10M18 20V4M6 20v-4"/>
  </svg>
);

const TrendingUpIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
    <polyline points="17 6 23 6 23 12"/>
  </svg>
);

const RefreshIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M23 4v6h-6"/>
    <path d="M1 20v-6h6"/>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
  </svg>
);

function SalesPrediction() {
  const [categories, setCategories] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [localites, setLocalites] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedDelegation, setSelectedDelegation] = useState("");
  const [selectedLocalite, setSelectedLocalite] = useState("");
  const [selectedMonth, setSelectedMonth] = useState("");
  const [predictionResult, setPredictionResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [featureImportance, setFeatureImportance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("predict");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/sales/categories")
      .then(res => res.json())
      .then(data => setCategories(data || []))
      .catch(err => console.error("Error loading categories:", err));

    fetch("http://127.0.0.1:8000/sales/delegations")
      .then(res => res.json())
      .then(data => setDelegations(data || []))
      .catch(err => console.error("Error loading delegations:", err));

    fetch("http://127.0.0.1:8000/sales/metrics")
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Error loading metrics:", err));

    fetch("http://127.0.0.1:8000/sales/feature-importance")
      .then(res => res.json())
      .then(data => setFeatureImportance(data))
      .catch(err => console.error("Error loading feature importance:", err));
  }, []);

  const handleDelegationChange = async (delegation) => {
    setSelectedDelegation(delegation);
    setSelectedLocalite("");
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/sales/localites?delegation=${delegation}`);
      const data = await response.json();
      setLocalites(data || []);
    } catch (err) {
      console.error("Error loading localites:", err);
      setLocalites([]);
    }
  };

  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  const handlePredict = async () => {
    if (selectedCategories.length === 0) {
      alert("Veuillez sélectionner au moins une catégorie");
      return;
    }

    setLoading(true);
    
    const requestBody = {
      categories: selectedCategories,
      delegation: selectedDelegation || null,
      localite: selectedLocalite || null,
      month: selectedMonth ? parseInt(selectedMonth) : null
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/sales/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      console.log("Prédiction reçue:", data);
      setPredictionResult(data);
      setActiveTab("results");
    } catch (err) {
      console.error("Error predicting:", err);
      alert("Erreur lors de la prédiction");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null) return '0,00 DT';
    return new Intl.NumberFormat('fr-TN', { style: 'currency', currency: 'TND' }).format(amount);
  };

  return (
    <div className="sales-container">
      <div className="sales-tabs">
        <button 
          className={`sales-tab ${activeTab === "predict" ? "active" : ""}`}
          onClick={() => setActiveTab("predict")}
        >
          <SalesIcon />
          <span>Prédiction</span>
        </button>
        <button 
          className={`sales-tab ${activeTab === "metrics" ? "active" : ""}`}
          onClick={() => setActiveTab("metrics")}
        >
          <ChartBarIcon />
          <span>Performance</span>
        </button>
        <button 
          className={`sales-tab ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
        >
          <TrendingUpIcon />
          <span>Résultats</span>
        </button>
      </div>

      {/* Onglet Prédiction */}
      {activeTab === "predict" && (
        <div className="sales-card">
          <div className="sales-card-header">
            <h2>Simulation de chiffre d'affaires</h2>
            <p>Estimez vos ventes potentielles par catégorie, région et période</p>
          </div>
          
          <div className="sales-form">
            <div className="form-section">
              <label className="form-section-label">
                <CategoryCheckIcon />
                <span>Catégories à analyser</span>
              </label>
              <div className="categories-container">
                {categories.length > 0 ? (
                  categories.map(cat => (
                    <label key={cat} className="category-option">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(cat)}
                        onChange={() => handleCategoryToggle(cat)}
                      />
                      <span>{cat}</span>
                    </label>
                  ))
                ) : (
                  <div className="loading-placeholder">Chargement des catégories...</div>
                )}
              </div>
            </div>

            <div className="form-row">
              <div className="form-field">
                <label className="form-field-label">
                  <LocationPinIcon />
                  <span>Délégation</span>
                </label>
                <select
                  value={selectedDelegation}
                  onChange={(e) => handleDelegationChange(e.target.value)}
                  className="sales-select"
                >
                  <option value="">Toutes les délégations</option>
                  {delegations.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <label className="form-field-label">
                  <LocationPinIcon />
                  <span>Localité</span>
                </label>
                <select
                  value={selectedLocalite}
                  onChange={(e) => setSelectedLocalite(e.target.value)}
                  className="sales-select"
                  disabled={!selectedDelegation}
                >
                  <option value="">Toutes les localités</option>
                  {localites.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <label className="form-field-label">
                  <CalendarIcon />
                  <span>Mois</span>
                </label>
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="sales-select"
                >
                  <option value="">Année complète</option>
                  {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            </div>

            <button 
              className="sales-button" 
              onClick={handlePredict}
              disabled={loading || selectedCategories.length === 0}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Calcul en cours...
                </>
              ) : (
                <>
                  <TrendingUpIcon />
                  Estimer le chiffre d'affaires
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Onglet Performance du modèle */}
      {activeTab === "metrics" && metrics && (
        <div className="sales-card">
          <div className="sales-card-header">
            <h2>Performance du modèle prédictif</h2>
            <p>Évaluation de la précision sur données d'entraînement et de test</p>
          </div>
          
          <div className="metrics-comparison">
            <div className="metric-box train">
              <div className="metric-box-header">Entraînement</div>
              <div className="metric-box-value">{(metrics.train?.r2 * 100).toFixed(1)}%</div>
              <div className="metric-box-label">R² Score</div>
              <div className="metric-box-detail">MAE: {formatCurrency(metrics.train?.mae)}</div>
              <div className="metric-box-detail">RMSE: {formatCurrency(metrics.train?.rmse)}</div>
            </div>
            
            <div className="metric-arrow">→</div>
            
            <div className="metric-box test">
              <div className="metric-box-header">Validation</div>
              <div className="metric-box-value">{(metrics.test?.r2 * 100).toFixed(1)}%</div>
              <div className="metric-box-label">R² Score</div>
              <div className="metric-box-detail">MAE: {formatCurrency(metrics.test?.mae)}</div>
              <div className="metric-box-detail">RMSE: {formatCurrency(metrics.test?.rmse)}</div>
            </div>
          </div>

          {featureImportance && Object.keys(featureImportance).length > 0 && (
            <div className="feature-importance-section">
              <h3 className="section-subtitle">Variables influentes</h3>
              <div className="features-list">
                {Object.entries(featureImportance).slice(0, 8).map(([feature, importance]) => (
                  <div key={feature} className="feature-row">
                    <span className="feature-name">{feature}</span>
                    <div className="feature-progress">
                      <div className="feature-progress-bar" style={{ width: `${importance * 100}%` }} />
                    </div>
                    <span className="feature-percent">{(importance * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Onglet Résultats */}
      {activeTab === "results" && predictionResult && (
        <div className="sales-card">
          <div className="sales-card-header">
            <h2>Projection du chiffre d'affaires</h2>
            <p>Estimation basée sur les données historiques et les tendances de vente</p>
          </div>
          
          {predictionResult.note && (
            <div className="info-message">
              <span>ℹ️</span> {predictionResult.note}
            </div>
          )}
          
          <div className="total-revenue">
            <div className="total-revenue-label">Chiffre d'affaires estimé</div>
            <div className="total-revenue-value">{formatCurrency(predictionResult.total_chiffre_affaires)}</div>
            <div className="total-revenue-period">
              {predictionResult.nombre_categories} catégorie(s) analysée(s)
            </div>
          </div>

          <div className="categories-breakdown">
            <h3 className="section-subtitle">Détail par catégorie</h3>
            {predictionResult.predictions && predictionResult.predictions.length > 0 ? (
              predictionResult.predictions.map((pred, idx) => (
                <div key={idx} className="category-item">
                  <div className="category-item-header">
                    <span className="category-item-name">{pred.categorie}</span>
                    <span className="category-item-amount">
                      {formatCurrency(pred.chiffre_affaires_predit)} <span className="per-period">/ mois</span>
                    </span>
                  </div>
                  {pred.details && pred.details.length > 0 && (
                    <div className="category-item-details">
                      {pred.details.slice(0, 4).map((detail, didx) => (
                        <span key={didx} className="month-detail">
                          Mois {detail.month}: {formatCurrency(detail.chiffre_affaires_predit)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="empty-state">Aucune prédiction disponible</div>
            )}
          </div>

          <button 
            className="reset-button"
            onClick={() => {
              setActiveTab("predict");
              setPredictionResult(null);
            }}
          >
            <RefreshIcon />
            Nouvelle simulation
          </button>
        </div>
      )}
    </div>
  );
}

export default SalesPrediction;