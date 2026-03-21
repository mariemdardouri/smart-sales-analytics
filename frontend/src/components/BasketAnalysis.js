import React, { useState, useEffect } from "react";
import "./BasketAnalysis.css";

function BasketAnalysis() {
  const [categories, setCategories] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedDelegation, setSelectedDelegation] = useState("");
  const [topProducts, setTopProducts] = useState([]);
  const [product1Input, setProduct1Input] = useState("");
  const [product2Input, setProduct2Input] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
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

  const handleAnalyzePair = () => {
    if (!product1Input.trim() || !product2Input.trim()) {
      alert("Veuillez saisir les deux produits à analyser");
      return;
    }
    
    setLoading(true);
    fetch("http://127.0.0.1:8000/analyze-pair", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ produits: [product1Input.trim(), product2Input.trim()] })
    })
      .then(res => res.json())
      .then(data => {
        setAnalysisResult(data);
        setLoading(false);
        setActiveTab("analyze");
      })
      .catch(err => {
        console.error("Error analyzing pair:", err);
        alert("Erreur lors de l'analyse");
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
          className={`tab-button ${activeTab === "analyze" ? "active" : ""}`}
          onClick={() => setActiveTab("analyze")}
        >
          Analyser une paire
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

      {/* Onglet Analyser une paire */}
      {activeTab === "analyze" && (
        <div className="analysis-card">
          <div className="analyze-group">
            <label className="filter-label">
              Analyser deux produits
            </label>
            <div className="pair-input-group">
              <input
                type="text"
                className="text-input"
                placeholder="Premier produit (ex: Fromage)"
                value={product1Input}
                onChange={e => setProduct1Input(e.target.value)}
              />
              <span className="pair-separator">+</span>
              <input
                type="text"
                className="text-input"
                placeholder="Deuxième produit (ex: Shampoing)"
                value={product2Input}
                onChange={e => setProduct2Input(e.target.value)}
              />
              <button className="primary-button" onClick={handleAnalyzePair}>
                Analyser
              </button>
            </div>
          </div>

          {loading && <div className="loading-spinner">Analyse en cours...</div>}

          {analysisResult && !loading && (
            <div className="analysis-result">
              <div className={`result-header ${analysisResult.sont_souvent_ensemble ? 'warning' : 'success'}`}>
                <h3>Résultat de l'analyse</h3>
              </div>
              
              <div className="result-content">
                <div className="product-pair-result">
                  <span className="product-highlight">{analysisResult.produit1}</span>
                  <span className="vs">vs</span>
                  <span className="product-highlight">{analysisResult.produit2}</span>
                </div>
                
                <div className="confidence-meter">
                  <div className="confidence-label">
                    Confiance: {analysisResult.confidence}%
                  </div>
                  <div className="confidence-bar">
                    <div 
                      className={`confidence-fill ${analysisResult.confidence >= 15 ? 'high' : analysisResult.confidence >= 5 ? 'medium' : 'low'}`}
                      style={{ width: `${Math.min(analysisResult.confidence, 100)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="recommendation-box">
                  <p className="recommendation-text">{analysisResult.recommandation}</p>
                </div>
                
                {analysisResult.details && analysisResult.details.conseil && (
                  <div className="advice-box">
                    <strong>💡 Conseil de placement:</strong>
                    <p>{analysisResult.details.conseil}</p>
                  </div>
                )}
                
                <div className="stats-details">
                  <h4>Détails statistiques</h4>
                  <ul>
                    <li>Fréquence d'achat de "{analysisResult.produit1}": {analysisResult.frequence_produit1} fois</li>
                    <li>Fréquence d'achat de "{analysisResult.produit2}": {analysisResult.frequence_produit2} fois</li>
                    <li>Achetés ensemble: {analysisResult.frequence_ensemble} fois</li>
                    <li>Probabilité d'achat ensemble: {analysisResult.confidence}%</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BasketAnalysis;