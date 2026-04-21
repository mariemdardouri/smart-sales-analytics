import React, { useEffect, useState } from "react";
import API from "../services/api";
import { Bar, Pie, Line, Doughnut } from "react-chartjs-2";
import "chart.js/auto";
import "./Dashboard.css";

const BLEU = ["#1f3864","#2e75b6","#2e86c1","#5dade2","#85c1e9","#aed6f1","#d6eaf8","#1a5276","#154360","#1b4f72"];

function fmt(val) {
  if (val === undefined || val === null) return "—";
  if (val >= 1_000_000) return (val / 1_000_000).toFixed(2) + "M";
  if (val >= 1_000) return (val / 1_000).toFixed(0) + "K";
  return parseFloat(val).toFixed(2);
}

export default function Dashboard() {
  const [section, setSection] = useState("produit");

  const [produitKPI, setProduitKPI] = useState({});
  const [tempsKPI, setTempsKPI]     = useState({});
  const [geoKPI, setGeoKPI]         = useState({});

  const [caProduit, setCaProduit]           = useState({});
  const [caCategorie, setCaCategorie]       = useState({});
  const [prixMoyenCat, setPrixMoyenCat]     = useState({});
  const [caMarque, setCaMarque]             = useState({});

  const [caMois, setCaMois]           = useState({});
  const [caSaison, setCaSaison]       = useState({});
  const [caTrimestre, setCaTrimestre] = useState({});

  const [caDelegation, setCaDelegation]           = useState({});
  const [caLocalite, setCaLocalite]               = useState({});
  const [clientsDelegation, setClientsDelegation] = useState({});

  const [selectedDelegation, setSelectedDelegation] = useState("ALL");
  const [selectedLocalite, setSelectedLocalite] = useState("ALL");

  useEffect(() => {
    API.get("/analytics/produit/kpi").then(r => setProduitKPI(r.data)).catch(console.error);
    API.get("/analytics/produit/ca-produit").then(r => setCaProduit(r.data)).catch(console.error);
    API.get("/analytics/produit/ca-categorie").then(r => setCaCategorie(r.data)).catch(console.error);
    API.get("/analytics/produit/prix-moyen-categorie").then(r => setPrixMoyenCat(r.data)).catch(console.error);
    API.get("/analytics/produit/ca-marque").then(r => setCaMarque(r.data)).catch(console.error);

    API.get("/analytics/temps/kpi").then(r => setTempsKPI(r.data)).catch(console.error);
    API.get("/analytics/temps/mois").then(r => setCaMois(r.data)).catch(console.error);
    API.get("/analytics/temps/saison").then(r => setCaSaison(r.data)).catch(console.error);
    API.get("/analytics/temps/trimestre").then(r => setCaTrimestre(r.data)).catch(console.error);

    API.get("/analytics/geo/kpi").then(r => setGeoKPI(r.data)).catch(console.error);
    API.get("/analytics/geo/ca-delegation").then(r => setCaDelegation(r.data)).catch(console.error);
    API.get("/analytics/geo/ca-localite").then(r => setCaLocalite(r.data)).catch(console.error);
    API.get("/analytics/geo/clients-delegation").then(r => setClientsDelegation(r.data)).catch(console.error);
  }, []);

  /* ---- shared chart options ---- */
  const barH = {
    indexAxis: "y",
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { grid: { color: "#e5e7eb" } }, y: { grid: { display: false } } },
  };
  const barV = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { grid: { display: false } }, y: { grid: { color: "#e5e7eb" } } },
  };
  const lineOpts = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { grid: { display: false } }, y: { grid: { color: "#e5e7eb" } } },
    elements: { line: { tension: 0.4 } },
  };
  const pieOpts = {
    responsive: true,
    plugins: { legend: { position: "right" } },
  };

  return (
    <div className="power-dashboard">

      {/* ===== TABS ===== */}
      <div className="dashboard-tabs">
        <button onClick={() => setSection("produit")} className={section === "produit" ? "active" : ""}>
          📦 Analyse Produit
        </button>
        <button onClick={() => setSection("temps")} className={section === "temps" ? "active" : ""}>
          ⏱ Analyse Temps
        </button>
        <button onClick={() => setSection("geo")} className={section === "geo" ? "active" : ""}>
          🌍 Analyse Géographique
        </button>
      </div>

      {/* ============================= PRODUIT ============================= */}
      {section === "produit" && (
        <section className="section">
          {/* KPIs — 3 large tiles */}
          <div className="kpi-row">
            <div className="kpi-card">
              <div className="kpi-value">{fmt(produitKPI.ca_total)}</div>
              <div className="kpi-label">Chiffre Affaires</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-value">{produitKPI.nb_marques ?? "—"}</div>
              <div className="kpi-label">Nombre Marque</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-value">{produitKPI.nb_produits ?? "—"}</div>
              <div className="kpi-label">Nombre Produit</div>
            </div>
          </div>

          {/* 2×2 chart grid */}
          <div className="grid-2x2">
            {/* Horizontal bar — CA par produit */}
            <div className="card">
              <h3 className="center-title">Chiffre Affaires par nom produit</h3>
              <Bar
                data={{
                  labels: (caProduit.labels || []).slice(0, 10),
                  datasets: [{
                    data: (caProduit.values || []).slice(0, 10),
                    backgroundColor: "#1f3864",
                    borderRadius: 3,
                  }]
                }}
                options={{
                  ...barH,
                  maintainAspectRatio: false
                }}

              />
            </div>

            {/* Pie — CA par catégorie */}
            <div className="card">
              <h3>Chiffre Affaires par catégorie</h3>
              <Pie
                data={{
                  labels: Object.keys(caCategorie || {}),
                  datasets: [{ data: Object.values(caCategorie || {}), backgroundColor: BLEU }]
                }}
                options={pieOpts}
              />
            </div>

            {/* Doughnut — Prix moyen par catégorie */}
            <div className="card">
              <h3>Prix Moyen par catégorie</h3>
              <Doughnut
                data={{
                  labels: Object.keys(prixMoyenCat || {}),
                  datasets: [{ data: Object.values(prixMoyenCat || {}), backgroundColor: BLEU }]
                }}
                options={pieOpts}
              />
            </div>

            {/* Vertical bar — CA par marque */}
            <div className="card">
              <h3>Chiffre Affaires par marque</h3>
              <Bar
                data={{
                  labels: (caMarque.labels || []).slice(0, 15),
                  datasets: [{
                    data: (caMarque.values || []).slice(0, 15),
                    backgroundColor: "#2e75b6",
                    borderRadius: 3,
                  }]
                }}
                options={barV}
              />
            </div>
          </div>
        </section>
      )}

      {/* ============================= TEMPS ============================= */}
      {section === "temps" && (
        <section className="section">
          {/* KPIs — big CA + two stacked on the right */}
          <div className="kpi-row temps-kpi">
            <div className="kpi-card large-kpi">
              <div className="kpi-value">{fmt(tempsKPI.ca_total)}</div>
              <div className="kpi-label">Chiffre Affaires</div>
            </div>
            <div className="kpi-stack">
              <div className="kpi-card">
                <div className="kpi-value">{fmt(tempsKPI.panier_moyen)}</div>
                <div className="kpi-label">Panier Moyen</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-value">{fmt(tempsKPI.nb_transactions)}</div>
                <div className="kpi-label">Nombre de Transactions</div>
              </div>
            </div>
          </div>

          {/* Top row: doughnut + horizontal bar side by side */}
          <div className="grid-2x1">
            <div className="card">
              <h3>Chiffre Affaires par Trimestre</h3>
              <Doughnut
                data={{
                  labels: Object.keys(caTrimestre || {}).map(k => `T${k}`),
                  datasets: [{
                    data: Object.values(caTrimestre || {}),
                    backgroundColor: ["#1f3864","#2e75b6","#5dade2","#aed6f1"],
                  }]
                }}
                options={pieOpts}
              />
            </div>

            <div className="card">
              <h3>Chiffre Affaires par Saison</h3>
              <Bar
                data={{
                  labels: Object.keys(caSaison || {}),
                  datasets: [{
                    data: Object.values(caSaison || {}),
                    backgroundColor: "#1f3864",
                    borderRadius: 3,
                  }]
                }}
                options={barH}
              />
            </div>
          </div>

          {/* Full-width line chart */}
          <div className="card mt-20">
            <h3>Chiffre Affaires par Mois</h3>
            <Line
              data={{
                labels: caMois.labels || [],
                datasets: [{
                  label: "CA",
                  data: caMois.values || [],
                  borderColor: "#1f3864",
                  backgroundColor: "rgba(31,56,100,0.08)",
                  fill: true,
                  pointBackgroundColor: "#1f3864",
                }]
              }}
              options={lineOpts}
            />
          </div>
        </section>
      )}

      {/* ============================= GEO ============================= */}
      {section === "geo" && (
        <section className="section">
          {/* KPIs */}
          <div className="kpi-row geo-kpi">
            <div className="kpi-card">
              <div className="kpi-value">{geoKPI.nb_localites ?? "—"}</div>
              <div className="kpi-label">Nombre Total de Localités</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-value">{geoKPI.nb_delegations ?? "—"}</div>
              <div className="kpi-label">Nombre Total de Délégations</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-value">{geoKPI.nb_clients ?? "—"}</div>
              <div className="kpi-label">Nombre de Clients Actifs</div>
            </div>
          </div>

          {/* Full-width bar — clients par délégation */}
          <div className="card mb-20">
            <h3>Nombre de Clients Actifs par Délégation</h3>
            <Bar
              data={{
                labels: Object.keys(clientsDelegation || {}),
                datasets: [{
                  data: Object.values(clientsDelegation || {}),
                  backgroundColor: "#1f3864",
                  borderRadius: 3,
                }]
              }}
              options={barV}
            />
          </div>

          {/* Pie + Doughnut side by side */}
          <div className="grid-2x1">

            {/* ================== DELEGATION ================== */}
            <div className="card">
              <h3>Chiffre Affaires par Délégation</h3>

              <Pie
                data={{
                  labels: Object.entries(caDelegation || {})
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .filter(([k]) =>
                      selectedDelegation === "ALL" || k === selectedDelegation
                    )
                    .map(([k]) => k),

                  datasets: [{
                    data: Object.entries(caDelegation || {})
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 10)
                      .filter(([k]) =>
                        selectedDelegation === "ALL" || k === selectedDelegation
                      )
                      .map(([, v]) => v),

                    backgroundColor: BLEU
                  }]
                }}
                options={pieOpts}
              />
            </div>

            {/* ================== LOCALITE ================== */}
            <div className="card">
              <h3>Chiffre Affaires par Localité</h3>

              <Doughnut
                data={{
                  labels: Object.entries(caLocalite || {})
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .filter(([k]) =>
                      selectedLocalite === "ALL" || k === selectedLocalite
                    )
                    .map(([k]) => k),

                  datasets: [{
                    data: Object.entries(caLocalite || {})
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 10)
                      .filter(([k]) =>
                        selectedLocalite === "ALL" || k === selectedLocalite
                      )
                      .map(([, v]) => v),

                    backgroundColor: BLEU
                  }]
                }}
                options={pieOpts}
              />
            </div>

          </div>
        </section>
      )}
    </div>
  );
}