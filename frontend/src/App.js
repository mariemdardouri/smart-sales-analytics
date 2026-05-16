import React, { useState, useEffect } from "react";

import Home from "./components/Home";
import Login from "./components/Login";
import Signup from "./components/Signup";

import BasketAnalysis from "./components/BasketAnalysis";
import Prediction from "./components/Prediction";
import SalesPrediction from "./components/SalesPrediction";
import LocationOptimizer from "./components/LocationOptimizer";
import Dashboard from "./components/Dashboard";
import Chatbot from "./components/Chatbot";
import AdminUsers from "./components/AdminUsers";

import "./App.css";

// ==================== ICÔNES SVG ====================
const DashboardIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1"/>
    <rect x="14" y="3" width="7" height="7" rx="1"/>
    <rect x="14" y="14" width="7" height="7" rx="1"/>
    <rect x="3" y="14" width="7" height="7" rx="1"/>
  </svg>
);

const BasketIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="9" cy="21" r="1"/>
    <circle cx="20" cy="21" r="1"/>
    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
  </svg>
);

const PredictionIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4-3-9s1.34-9 3-9"/>
  </svg>
);

const SalesIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2v20M17 7l-5-5-5 5M7 17l5 5 5-5"/>
  </svg>
);

const LocationIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
);

const AdminIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);

const LogoutIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
    <polyline points="16 17 21 12 16 7"/>
    <line x1="21" y1="12" x2="9" y2="12"/>
  </svg>
);

const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

// ==================== APP ====================
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [currentAuthPage, setCurrentAuthPage] = useState("home");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("user_role");
    const name = localStorage.getItem("user_name");

    if (token && role) {
      setIsAuthenticated(true);
      setUser({ role, name });
    }
  }, []);

  // ---------------- AUTH ----------------
  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
    setPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_role");
    localStorage.removeItem("user_name");
    setIsAuthenticated(false);
    setUser(null);
    setCurrentAuthPage("home");
  };

  // ---------------- AUTH PAGES ----------------
  if (!isAuthenticated && currentAuthPage === "home") {
    return (
      <Home
        onLoginClick={() => setCurrentAuthPage("login")}
        onSignupClick={() => setCurrentAuthPage("signup")}
      />
    );
  }

  if (!isAuthenticated && currentAuthPage === "login") {
    return (
      <Login
        onLogin={(data) => {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("user_role", data.role);
          setUser({
            role: data.role,
            name: data.username,
          });
          setIsAuthenticated(true);
          setPage("dashboard");
        }}
        goSignup={() => setCurrentAuthPage("signup")}
      />
    );
  }

  if (!isAuthenticated && currentAuthPage === "signup") {
    return <Signup goLogin={() => setCurrentAuthPage("login")} />;
  }

  // ---------------- MENU BY ROLE ----------------
  const isAdmin = user?.role === "admin";

  const menuItems = isAdmin
    ? [
        { id: "dashboard", label: "Dashboard", icon: <DashboardIcon /> },
        { id: "admin", label: "Gestion Utilisateurs", icon: <AdminIcon /> },
      ]
    : [
        { id: "dashboard", label: "Dashboard", icon: <DashboardIcon /> },
        { id: "basket", label: "Analyse Panier", icon: <BasketIcon /> },
        { id: "prediction", label: "Prédiction Produits", icon: <PredictionIcon /> },
        { id: "sales", label: "Prédiction Ventes", icon: <SalesIcon /> },
        { id: "location", label: "Où vendre ?", icon: <LocationIcon /> },
      ];

  return (
    <div className="app-container">
      <Chatbot />

      {/* SIDEBAR */}
      <aside className="sidebar">
        <h2 className="logo">Smart Sales Analytics</h2>

        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            className={page === item.id ? "active" : ""}
          >
            <span className="menu-icon">{item.icon}</span>
            <span className="menu-label">{item.label}</span>
          </button>
        ))}
        <hr />

        <button onClick={handleLogout} className="logout-btn">
          <span className="menu-icon"><LogoutIcon /></span>
          <span className="menu-label">Déconnexion</span>
        </button>
      </aside>

      {/* MAIN */}
      <div className="main">
        <header className="topbar">
          <h1>
            {page === "dashboard" && "Dashboard"}
            {page === "basket" && "Analyse Panier"}
            {page === "prediction" && "Prédiction Produits"}
            {page === "sales" && "Prédiction Ventes"}
            {page === "location" && "Optimisation Localisation"}
            {page === "admin" && "Gestion Utilisateurs"}
          </h1>

          <div className="user-info">
            <span className="user-icon"><UserIcon /></span>
            <span className="user-name">{user?.name}</span>
            <span className={`user-role ${isAdmin ? "admin" : "user"}`}>
              {user?.role === "admin" ? "Administrateur" : "Utilisateur"}
            </span>
          </div>
        </header>

        <div className="content">
          {page === "admin" && isAdmin && <AdminUsers />}
          {page === "dashboard" && <Dashboard />}
          {!isAdmin && page === "basket" && <BasketAnalysis />}
          {!isAdmin && page === "prediction" && <Prediction />}
          {!isAdmin && page === "sales" && <SalesPrediction />}
          {!isAdmin && page === "location" && <LocationOptimizer />}
        </div>
      </div>
    </div>
  );
}

export default App;