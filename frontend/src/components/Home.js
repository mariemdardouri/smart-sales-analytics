import React from "react";
import "./Home.css";

function Home({ onLoginClick, onSignupClick }) {
  return (
    <div className="premium-home">
      {/* Hero Section avec animation */}
      <div className="premium-hero">
        <div className="premium-nav">
          <div className="nav-brand">
            <span className="brand-icon"> <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 2L2 9L16 16L30 9L16 2Z" stroke="white" strokeWidth="1.5" fill="none"/>
              <path d="M2 23L16 30L30 23" stroke="white" strokeWidth="1.5" fill="none"/>
              <path d="M2 16L16 23L30 16" stroke="white" strokeWidth="1.5" fill="none"/>
            </svg></span>
            <span className="brand-name">SmartSales</span>
          </div>
          <div className="nav-actions">
            <button className="nav-login" onClick={onLoginClick}>Connexion</button>
            <button className="nav-signup" onClick={onSignupClick}>Essai gratuit</button>
          </div>
        </div>

        <div className="premium-hero-content">
          <div className="hero-badge">
            <span className="pulse-dot"></span>
            Analyse prédictive nouvelle génération
          </div>
          <h1 className="hero-main-title">
            Transformez vos données de vente<br />
            en <span className="gradient">décisions stratégiques</span>
          </h1>
          <p className="hero-description">
            Smart Sales Analytics utilise l'intelligence artificielle pour analyser vos ventes,
            prédire vos performances et optimiser votre stratégie commerciale.
          </p>
          <div className="hero-cta">
            <button className="cta-primary" onClick={onSignupClick}>
              Commencer gratuitement
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4.16666 10H15.8333M15.8333 10L10 4.16669M15.8333 10L10 15.8334" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </button>
            <button className="cta-secondary" onClick={onLoginClick}>
              Se connecter
            </button>
          </div>
        </div>

        {/* Dashboard Preview animé */}
        <div className="dashboard-preview">
          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-dots">
                <span></span><span></span><span></span>
              </div>
              <div className="preview-title">Dashboard SmartSales</div>
            </div>
            <div className="preview-chart">
              <div className="chart-bar" style={{ height: '60%' }}></div>
              <div className="chart-bar" style={{ height: '80%' }}></div>
              <div className="chart-bar" style={{ height: '45%' }}></div>
              <div className="chart-bar" style={{ height: '90%' }}></div>
              <div className="chart-bar" style={{ height: '70%' }}></div>
              <div className="chart-bar" style={{ height: '55%' }}></div>
            </div>
            <div className="preview-stats">
              <div className="stat-box"></div>
              <div className="stat-box"></div>
              <div className="stat-box"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
<div className="premium-features">
  <div className="features-header">
    <span className="features-badge">Fonctionnalités clés</span>
    <h2>Conçu pour les équipes data-driven</h2>
    <p>Des outils puissants pour transformer vos données en décisions stratégiques</p>
  </div>
  
  <div className="features-container">
    <div className="feature-card">
      <div className="feature-icon-wrapper">
        <svg className="feature-svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect x="4" y="12" width="6" height="16" rx="1" fill="currentColor"/>
          <rect x="13" y="8" width="6" height="20" rx="1" fill="currentColor"/>
          <rect x="22" y="4" width="6" height="24" rx="1" fill="currentColor"/>
        </svg>
      </div>
      <h3>Analyse de panier</h3>
      <p>Découvrez les associations de produits grâce à nos algorithmes de machine learning avancés.</p>
      <div className="feature-hover-effect"></div>
    </div>

    <div className="feature-card featured-mid">
      <div className="feature-icon-wrapper">
        <svg className="feature-svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path d="M4 20L9 15L14 18L22 8L28 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          <path d="M28 14V20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M22 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </div>
      <h3>Prédiction ML</h3>
      <p>Anticipez vos ventes avec une précision inégalée grâce à nos modèles propriétaires.</p>
      <div className="feature-hover-effect"></div>
    </div>

    <div className="feature-card">
      <div className="feature-icon-wrapper">
        <svg className="feature-svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="12" r="4" stroke="currentColor" strokeWidth="2" fill="none"/>
          <path d="M8 28L16 20L24 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          <path d="M4 8L12 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M20 8L28 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </div>
      <h3>Optimisation régionale</h3>
      <p>Identifiez les zones à fort potentiel pour maximiser votre retour sur investissement.</p>
      <div className="feature-hover-effect"></div>
    </div>
  </div>
   </div>
    </div>
  );
}

export default Home;