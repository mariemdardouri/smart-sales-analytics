import React, { useState, useEffect } from "react";
import "./BasketAnalysis.css";

// Icônes SVG
const ProductsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="9" y="2" width="6" height="6" rx="1"/>
    <rect x="4" y="10" width="16" height="12" rx="2"/>
    <line x1="9" y1="16" x2="15" y2="16"/>
  </svg>
);

const CategoriesIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 4h16v16H4z"/>
    <path d="M9 8h6"/>
    <path d="M9 12h6"/>
  </svg>
);

const InfoIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="12" x2="12" y2="16"/>
    <line x1="12" y1="8" x2="12.01" y2="8"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <circle cx="12" cy="16" r="0.5" fill="currentColor" stroke="none"/>
  </svg>
);

const CloseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

function BasketAnalysis() {

  const [categories, setCategories] = useState([]);
  const [delegations, setDelegations] = useState([]);

  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedDelegation, setSelectedDelegation] = useState("");

  const [placementSuggestions, setPlacementSuggestions] = useState(null);
  const [layoutSuggestions, setLayoutSuggestions] = useState(null);

  const [loading, setLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState("products");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/categories")
      .then(res => res.json())
      .then(data => setCategories(data));

    fetch("http://127.0.0.1:8000/delegations")
      .then(res => res.json())
      .then(data => setDelegations(data));
  }, []);

  const handleProductAnalysis = async () => {
    setLoading(true);
    let url = `http://127.0.0.1:8000/placement/recommendations?top_n=10`;

    if (selectedCategory) url += `&categorie=${encodeURIComponent(selectedCategory)}`;
    if (selectedDelegation) url += `&delegation=${encodeURIComponent(selectedDelegation)}`;

    try {
      const res = await fetch(url);
      const data = await res.json();
      setPlacementSuggestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLayoutAnalysis = async () => {
    setLoading(true);
    let url = `http://127.0.0.1:8000/layout/recommendations`;

    try {
      const res = await fetch(url);
      const data = await res.json();
      setLayoutSuggestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Déterminer la recommandation en fonction du lift (caché à l'utilisateur)
  const getRecommendation = (lift) => {
    if (lift < 0.85) {
      return {
        action: "À rapprocher",
        description: "Ces catégories sont rarement achetées ensemble",
        placement: "Placez-les côte à côte pour encourager la découverte",
        icon: <CheckIcon />
      };
    } else if (lift < 0.95) {
      return {
        action: "Placement libre",
        description: "Association neutre, pas de contrainte particulière",
        placement: "Peuvent être placées dans la même zone",
        icon: <InfoIcon />
      };
    } else {
      return {
        action: "À éloigner",
        description: "Ces catégories sont souvent achetées ensemble",
        placement: "Disposez-les aux extrémités opposées du magasin",
        icon: <AlertIcon />
      };
    }
  };

  return (
    <div className="basket-analysis">
      <div className="top-header">
        <div>
          <h1>Optimisation du placement</h1>
          <p>Recommandations intelligentes pour organiser votre espace de vente</p>
        </div>
      </div>

      <div className="mode-selector">
        <button
          className={analysisMode === "products" ? "active-mode" : ""}
          onClick={() => setAnalysisMode("products")}
        >
          <ProductsIcon />
          <span>Par produit</span>
        </button>
        <button
          className={analysisMode === "layout" ? "active-mode" : ""}
          onClick={() => setAnalysisMode("layout")}
        >
          <CategoriesIcon />
          <span>Par catégorie</span>
        </button>
      </div>

      <div className="analysis-card">
        <div className="filters-row">
          {analysisMode === "products" && (
            <div className="filter-box">
              <label>Catégorie</label>
              <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
                <option value="">Toutes les catégories</option>
                {categories.map((cat, i) => (
                  <option key={i} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          )}

          {analysisMode === "products" && (
            <div className="filter-box">
              <label>Délégation</label>
              <select value={selectedDelegation} onChange={(e) => setSelectedDelegation(e.target.value)}>
                <option value="">Toutes les délégations</option>
                {delegations.map((d, i) => (
                  <option key={i} value={d}>{d}</option>
                ))}
              </select>
            </div>
          )}

          {analysisMode === "layout" && (
            <div className="info-banner">
              <InfoIcon />
              <span>Analyse basée sur l'ensemble des données pour un plan général</span>
            </div>
          )}

          <button className="analyze-btn" onClick={analysisMode === "products" ? handleProductAnalysis : handleLayoutAnalysis}>
            {loading ? "Analyse en cours..." : "Lancer l'analyse"}
          </button>
        </div>

        {loading && <div className="loading-box">Analyse des données en cours...</div>}

        {/* Analyse Produits */}
        {analysisMode === "products" && placementSuggestions && !loading && (
          <>
            {placementSuggestions.a_eloigner?.length > 0 && (
              <ResultSection
                title="Produits à éloigner"
                description="Ces produits sont souvent achetés ensemble, séparez-les pour maximiser le panier moyen"
                items={placementSuggestions.a_eloigner}
                type="alert"
                icon={<AlertIcon />}
              />
            )}
            {placementSuggestions.a_rapprocher?.length > 0 && (
              <ResultSection
                title="Produits à rapprocher"
                description="Ces produits sont rarement achetés ensemble, rapprochez-les pour stimuler la découverte"
                items={placementSuggestions.a_rapprocher}
                type="success"
                icon={<CheckIcon />}
              />
            )}
          </>
        )}

        {/* Analyse Catégories */}
        {analysisMode === "layout" && layoutSuggestions && !loading && (
          <div className="layout-recommendations">
            
            {/* Plan d'action */}
            <div className="action-plan">
              <h3>Plan de disposition recommandé</h3>
              <div className="plan-steps">
                {layoutSuggestions.plan_suggestion?.map((step, idx) => (
                  <div key={idx} className="plan-step">
                    <span className="step-num">{idx + 1}</span>
                    <span className="step-text">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Toutes les catégories classées par recommandation */}
            <div className="recommendations-lists">
              {[...(layoutSuggestions.zones_a_rapprocher || []), ...(layoutSuggestions.zones_a_eloigner || [])]
                .sort((a, b) => a.lift - b.lift)
                .map((item, idx) => {
                  const rec = getRecommendation(item.lift);
                  const isAlert = rec.action === "À éloigner";
                  const isSuccess = rec.action === "À rapprocher";
                  
                  return (
                    <div key={idx} className={`recommendation-card ${isAlert ? 'alert' : isSuccess ? 'success' : 'neutral'}`}>
                      <div className="card-header">
                        <div className="card-icon">{rec.icon}</div>
                        <div className="card-action">{rec.action}</div>
                        <div className="card-pair">
                          <span className="cat-name">{item.description?.split(" et ")[0]}</span>
                          <span className="cat-separator">+</span>
                          <span className="cat-name">{item.description?.split(" et ")[1]}</span>
                        </div>
                      </div>
                      <div className="card-body">
                        <p className="card-description">{rec.description}</p>
                        <p className="card-placement">{rec.placement}</p>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ResultSection({ title, description, items, type, icon }) {
  if (!items?.length) return null;

  return (
    <div className="result-section">
      <div className={`section-header ${type}`}>
        <div className="header-icon">{icon}</div>
        <div className="header-text">
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
      </div>
      <div className="result-grid">
        {items.map((item, index) => (
          <div className="product-card" key={index}>
            <div className="card-rank">{index + 1}</div>
            <div className="card-pair">
              <span className="product-name">{item.produit1}</span>
              <span className="product-separator">+</span>
              <span className="product-name">{item.produit2}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default BasketAnalysis;