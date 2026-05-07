import React, { useState, useEffect } from "react";
import "./BasketAnalysis.css";

function BasketAnalysis() {
  const [categories, setCategories] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedDelegation, setSelectedDelegation] = useState("");
  const [topProducts, setTopProducts] = useState([]);
  const [placementSuggestions, setPlacementSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("top");
  const [topN, setTopN] = useState(5);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/categories")
      .then(res => res.json())
      .then(data => setCategories(data))
      .catch(err => console.error("Error loading categories:", err));

    fetch("http://127.0.0.1:8000/delegations")
      .then(res => res.json())
      .then(data => setDelegations(data))
      .catch(err => console.error("Error loading delegations:", err));
  }, []);

  const handleFetchBasket = () => {
    setLoading(true);
    let url = `http://127.0.0.1:8000/basket?top_n=${topN}`;
    if (selectedCategory) {
      url += `&categorie=${encodeURIComponent(selectedCategory)}`;
    }
    if (selectedDelegation) {
      url += `&delegation=${encodeURIComponent(selectedDelegation)}`;
    }
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setTopProducts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching top products:", err);
        setLoading(false);
      });
  };

  const handleGetPlacementSuggestions = () => {
    setLoading(true);
    let url = `http://127.0.0.1:8000/placement/recommendations?top_n=15`;
    if (selectedCategory) {
      url += `&categorie=${encodeURIComponent(selectedCategory)}`;
    }
    if (selectedDelegation) {
      url += `&delegation=${encodeURIComponent(selectedDelegation)}`;
    }
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setPlacementSuggestions(data);
        setLoading(false);
        setActiveTab("suggestions");
      })
      .catch(err => {
        console.error("Error fetching placement suggestions:", err);
        alert("Erreur lors de la génération des suggestions");
        setLoading(false);
      });
  };

  return (
    <div className="basket-analysis">
      <div className="tabs-container">
        <button 
          className={`tab-button ${activeTab === "top" ? "active" : ""}`}
          onClick={() => setActiveTab("top")}
        >
          Top produits ensemble
        </button>
        <button 
          className={`tab-button ${activeTab === "suggestions" ? "active" : ""}`}
          onClick={() => setActiveTab("suggestions")}
        >
          Suggestions placement
        </button>
      </div>

      {/* Onglet Top produits ensemble */}
      {activeTab === "top" && (
        <div className="analysis-card">
          <div className="filters-group">
            <div className="filter-item">
              <label htmlFor="category-select" className="filter-label">
                Catégorie
              </label>
              <select
                id="category-select"
                className="filter-select"
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
              >
                <option value="">Toutes les catégories</option>
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="filter-item">
              <label htmlFor="delegation-select" className="filter-label">
                Délégation
              </label>
              <select
                id="delegation-select"
                className="filter-select"
                value={selectedDelegation}
                onChange={e => setSelectedDelegation(e.target.value)}
              >
                <option value="">Toutes les délégations</option>
                {delegations.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div className="filter-item">
              <label htmlFor="top-n" className="filter-label">
                Nombre de combinaisons
              </label>
              <input
                id="top-n"
                type="number"
                className="number-input"
                value={topN}
                onChange={e => setTopN(Math.max(1, parseInt(e.target.value) || 5))}
                min="1"
                max="20"
              />
            </div>

            <button className="primary-button" onClick={handleFetchBasket}>
              Analyser
            </button>
          </div>

          {loading && <div className="loading-spinner">Chargement...</div>}

          {topProducts.length > 0 && !loading && (
            <div className="products-list">
              <h3 className="list-title">
                Top {topProducts.length} combinaisons de produits
              </h3>
              <div className="product-grid">
                {topProducts.map((item, i) => (
                  <div key={i} className="product-card">
                    <div className="product-rank">{i + 1}</div>
                    <div className="product-pair">
                      {item.produits.map((prod, idx) => (
                        <React.Fragment key={idx}>
                          <span className="product-name">{prod}</span>
                          {idx < item.produits.length - 1 && (
                            <span className="product-plus">+</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Onglet Suggestions placement */}
      {activeTab === "suggestions" && (
        <div className="analysis-card">
          <div className="suggestions-header">
            <h3>🏪 Suggestions de placement en magasin</h3>
            <p className="suggestions-subtitle">
              Basé sur l'analyse des paniers d'achat : produits souvent achetés ensemble 
              (à rapprocher) ou rarement ensemble (à éloigner)
            </p>
          </div>

          <div className="filters-group">
            <div className="filter-item">
              <label className="filter-label">
                Catégorie
              </label>
              <select
                className="filter-select"
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
              >
                <option value="">Toutes les catégories</option>
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="filter-item">
              <label className="filter-label">
                Délégation
              </label>
              <select
                className="filter-select"
                value={selectedDelegation}
                onChange={e => setSelectedDelegation(e.target.value)}
              >
                <option value="">Toutes les délégations</option>
                {delegations.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <button className="primary-button" onClick={handleGetPlacementSuggestions}>
              Générer les suggestions
            </button>
          </div>

          {loading && <div className="loading-spinner">Génération des suggestions...</div>}

          {placementSuggestions && !loading && (
            <div className="placement-results">
              {/* Conseils généraux */}
              {placementSuggestions.conseils_generaux && placementSuggestions.conseils_generaux.length > 0 && (
                <div className="advice-section">
                  <h4 className="advice-section-title">💡 Conseils prioritaires</h4>
                  {placementSuggestions.conseils_generaux.map((conseil, idx) => (
                    <div key={idx} className={`advice-card ${conseil.type}`}>
                      <div className="advice-message">{conseil.message}</div>
                      <div className="advice-detail">{conseil.detail}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Produits à rapprocher */}
              {placementSuggestions.a_rapprocher && placementSuggestions.a_rapprocher.length > 0 && (
                <div className="recommendation-section">
                  <h4 className="section-title rapprocher-title">
                    🔥 Produits à RAPPROCHER (souvent achetés ensemble)
                  </h4>
                  <div className="product-grid">
                    {placementSuggestions.a_rapprocher.map((item, idx) => (
                      <div key={idx} className="product-card rapprocher-card">
                        <div className="product-rank">{idx + 1}</div>
                        <div className="product-pair">
                          <span className="product-name">{item.produit1}</span>
                          <span className="product-plus">+</span>
                          <span className="product-name">{item.produit2}</span>
                        </div>
                        <div className="placement-stats">
                          <span className="stat-badge">Lift: {item.lift}</span>
                          <span className="stat-badge">Confiance: {item.confiance}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {/* Produits à ÉLOIGNER (souvent achetés ensemble) */}
{placementSuggestions.a_eloigner && placementSuggestions.a_eloigner.length > 0 && (
  <div className="recommendation-section">
    <h4 className="section-title eloigner-title">
      ⚠️ Produits à ÉLOIGNER (souvent achetés ensemble)
    </h4>
    <div className="product-grid">
      {placementSuggestions.a_eloigner.map((item, idx) => (
        <div key={idx} className="product-card eloigner-card">
          <div className="product-rank">{idx + 1}</div>
          <div className="product-pair">
            <span className="product-name">{item.produit1}</span>
            <span className="product-plus">+</span>
            <span className="product-name">{item.produit2}</span>
          </div>
          <div className="placement-stats">
            <span className="stat-badge">Lift: {item.lift}</span>
            <span className="stat-badge">Confiance: {item.confiance}%</span>
          </div>
        </div>
      ))}
    </div>
  </div>
)}

{/* Produits à RAPPROCHER (rarement achetés ensemble) */}
{placementSuggestions.a_rapprocher && placementSuggestions.a_rapprocher.length > 0 && (
  <div className="recommendation-section">
    <h4 className="section-title rapprocher-title">
      ✅ Produits à RAPPROCHER (rarement achetés ensemble)
    </h4>
    <div className="product-grid">
      {placementSuggestions.a_rapprocher.map((item, idx) => (
        <div key={idx} className="product-card rapprocher-card">
          <div className="product-rank">{idx + 1}</div>
          <div className="product-pair">
            <span className="product-name">{item.produit1}</span>
            <span className="product-plus">+</span>
            <span className="product-name">{item.produit2}</span>
          </div>
          <div className="placement-stats">
            <span className="stat-badge">Lift: {item.lift}</span>
            <span className="stat-badge">Confiance: {item.confiance}%</span>
          </div>
        </div>
      ))}
    </div>
  </div>
)}

              {(!placementSuggestions.a_rapprocher || placementSuggestions.a_rapprocher.length === 0) && 
               (!placementSuggestions.a_eloigner || placementSuggestions.a_eloigner.length === 0) && (
                <div className="empty-state">
                  Aucune suggestion de placement pour les filtres sélectionnés
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BasketAnalysis;