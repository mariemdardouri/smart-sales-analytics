import React, { useState } from "react";
import "./AuthPremium.css";

function Login({ onLogin, goSignup }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Erreur de connexion");
        setLoading(false);
        return;
      }

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_role", data.role);
      localStorage.setItem("user_name", email.split("@")[0]);

      onLogin({
        token: data.access_token,
        role: data.role,
        name: email.split("@")[0]
      });

    } catch (err) {
      setError("Impossible de contacter le serveur");
      setLoading(false);
    }
  };

  return (
    <div className="auth-premium">
      <div className="auth-premium-left">
        <div className="auth-left-content">
          <div className="auth-logo">
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path d="M16 2L2 9L16 16L30 9L16 2Z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
    <path d="M2 23L16 30L30 23" stroke="currentColor" strokeWidth="1.5" fill="none"/>
    <path d="M2 16L16 23L30 16" stroke="currentColor" strokeWidth="1.5" fill="none"/>
  </svg>
  <span>SmartSales</span>
</div>
          <h2>Bienvenue</h2>
          <p>Connectez-vous pour accéder à votre espace</p>
          <div className="auth-features">
            <div className="auth-feature">✓ Analyse de panier avancée</div>
            <div className="auth-feature">✓ Prédiction ML </div>
            <div className="auth-feature">✓ Optimisation régionale</div>
          </div>
        </div>
      </div>
      <div className="auth-premium-right">
        <div className="auth-card-premium">
          <h2>Connexion</h2>
          <p className="auth-subtitle">Accédez à votre compte</p>
          
          <div className="auth-form-premium">
            <input
              type="email"
              placeholder="Email professionnel"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input-premium"
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input-premium"
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            />
            
            {error && <div className="auth-error-premium">{error}</div>}
            
            <button 
              className="auth-btn-premium"
              onClick={handleLogin}
              disabled={loading}
            >
              {loading ? "Connexion..." : "Se connecter"}
            </button>
            
            <p className="auth-footer-premium">
              Pas encore de compte ?{" "}
              <button className="auth-link-premium" onClick={goSignup}>
                Créer un compte
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;