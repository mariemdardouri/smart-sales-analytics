import React, { useState } from "react";
import "./AuthPremium.css";

function Signup({ goLogin }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSignup = async () => {
    if (!username || !email || !password) {
      setError("Tous les champs sont obligatoires");
      return;
    }
    if (password !== confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    if (password.length < 6) {
      setError("6 caractères minimum");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Erreur d'inscription");
        setLoading(false);
        return;
      }

      alert("✅ Compte créé avec succès !");
      goLogin();

    } catch (err) {
      setError("Erreur serveur");
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
          <h2>Rejoignez l'aventure</h2>
          <p>Créez votre compte gratuitement</p>
          <div className="auth-features">
            <div className="auth-feature">✓ Support prioritaire</div>
            <div className="auth-feature">✓ Toutes fonctionnalités</div>
          </div>
        </div>
      </div>
      <div className="auth-premium-right">
        <div className="auth-card-premium">
          <h2>Inscription</h2>
          <p className="auth-subtitle">Créez votre compte</p>
          
          <div className="auth-form-premium">
            <input
              type="text"
              placeholder="Nom d'utilisateur"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="auth-input-premium"
            />
            <input
              type="email"
              placeholder="Email professionnel"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input-premium"
            />
            <input
              type="password"
              placeholder="Mot de passe (6+ caractères)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input-premium"
            />
            <input
              type="password"
              placeholder="Confirmer le mot de passe"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="auth-input-premium"
              onKeyPress={(e) => e.key === 'Enter' && handleSignup()}
            />
            
            {error && <div className="auth-error-premium">{error}</div>}
            
            <button 
              className="auth-btn-premium"
              onClick={handleSignup}
              disabled={loading}
            >
              {loading ? "Inscription..." : "Créer mon compte"}
            </button>
            
            <p className="auth-footer-premium">
              Déjà un compte ?{" "}
              <button className="auth-link-premium" onClick={goLogin}>
                Se connecter
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Signup;