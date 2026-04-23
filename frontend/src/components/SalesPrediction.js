import React, { useState, useEffect } from "react";
import "./SalesPrediction.css";

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
        headers: {
          "Content-Type": "application/json",
        },
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
    <div className="sales-prediction">
      <div className="tabs-container">
        <button 
          className={`tab-button ${activeTab === "predict" ? "active" : ""}`}
          onClick={() => setActiveTab("predict")}
        >
          Prédiction des ventes
        </button>
        <button 
          className={`tab-button ${activeTab === "metrics" ? "active" : ""}`}
          onClick={() => setActiveTab("metrics")}
        >
          Performance du modèle
        </button>
        <button 
          className={`tab-button ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
        >
          Résultats
        </button>
      </div>

      {activeTab === "predict" && (
        <div className="prediction-card">
          <h2>📊 Prédiction du chiffre d'affaires</h2>
          
          <div className="form-group">
            <label>Catégories de produits *</label>
            <div className="categories-grid">
              {categories.length > 0 ? (
                categories.map(cat => (
                  <label key={cat} className="category-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(cat)}
                      onChange={() => handleCategoryToggle(cat)}
                    />
                    {cat}
                  </label>
                ))
              ) : (
                <div>Chargement des catégories...</div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label>Délégation (optionnel)</label>
            <select
              value={selectedDelegation}
              onChange={(e) => handleDelegationChange(e.target.value)}
              className="form-select"
            >
              <option value="">Toutes les délégations</option>
              {delegations.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Localité (optionnel)</label>
            <select
              value={selectedLocalite}
              onChange={(e) => setSelectedLocalite(e.target.value)}
              className="form-select"
              disabled={!selectedDelegation}
            >
              <option value="">Toutes les localités</option>
              {localites.map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Mois (optionnel)</label>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="form-select"
            >
              <option value="">Tous les mois</option>
              {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          <button 
            className="predict-button" 
            onClick={handlePredict}
            disabled={loading || selectedCategories.length === 0}
          >
            {loading ? "Prédiction en cours..." : "Prédire le chiffre d'affaires"}
          </button>
        </div>
      )}

      {activeTab === "metrics" && metrics && (
        <div className="metrics-card">
          <h2>📈 Performance du modèle</h2>
          
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Entraînement</h3>
              <div className="metric-value">R²: {metrics.train ? (metrics.train.r2 * 100).toFixed(1) : 'N/A'}%</div>
              <div className="metric-value">MAE: {formatCurrency(metrics.train?.mae)}</div>
              <div className="metric-value">RMSE: {formatCurrency(metrics.train?.rmse)}</div>
            </div>
            
            <div className="metric-card">
              <h3>Test</h3>
              <div className="metric-value">R²: {metrics.test ? (metrics.test.r2 * 100).toFixed(1) : 'N/A'}%</div>
              <div className="metric-value">MAE: {formatCurrency(metrics.test?.mae)}</div>
              <div className="metric-value">RMSE: {formatCurrency(metrics.test?.rmse)}</div>
            </div>
          </div>

          {featureImportance && Object.keys(featureImportance).length > 0 && (
            <div className="feature-importance">
              <h3>Importance des features</h3>
              <div className="features-list">
                {Object.entries(featureImportance).slice(0, 10).map(([feature, importance]) => (
                  <div key={feature} className="feature-item">
                    <span className="feature-name">{feature}</span>
                    <div className="feature-bar-container">
                      <div 
                        className="feature-bar" 
                        style={{ width: `${importance * 100}%` }}
                      ></div>
                    </div>
                    <span className="feature-value">{(importance * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "results" && predictionResult && (
        <div className="results-card">
          <h2>💰 Résultats de la prédiction</h2>
          
          {predictionResult.note && (
            <div className="note-info">
              ℹ️ {predictionResult.note}
            </div>
          )}
          
          <div className="total-card">
            <div className="total-label">Chiffre d'affaires mensuel prédit</div>
            <div className="total-value">{formatCurrency(predictionResult.total_chiffre_affaires)}</div>
            <div className="total-subtitle">pour {predictionResult.nombre_categories} catégorie(s)</div>
          </div>

          <div className="categories-results">
            <h3>Détail par catégorie</h3>
            {predictionResult.predictions && predictionResult.predictions.length > 0 ? (
              predictionResult.predictions.map((pred, idx) => (
                <div key={idx} className="category-result">
                  <div className="category-header">
                    <span className="category-name">{pred.categorie}</span>
                    <span className="category-total">
                      {formatCurrency(pred.chiffre_affaires_predit)} / mois
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">Aucune prédiction disponible</div>
            )}
          </div>

          <button 
            className="new-prediction-button"
            onClick={() => {
              setActiveTab("predict");
              setPredictionResult(null);
            }}
          >
            Nouvelle prédiction
          </button>
        </div>
      )}
    </div>
  );
}

export default SalesPrediction;