from utils.preprocessing import load_data
from itertools import combinations
from collections import Counter
import pandas as pd
import numpy as np
from models import BasketRecommender

df_all = load_data()


df_all["date_dachat"] = pd.to_datetime(df_all["date_dachat"], errors="coerce")

df_all["transaction"] = (
    df_all["client_id"].astype(str)
    + "_"
    + df_all["date_dachat"].dt.strftime("%Y-%m-%d")
)

recommender = BasketRecommender(model_path="models/basket_model.pkl")

print("Tentative de chargement du modèle existant...")
if not recommender.load_model():
    print("Aucun modèle trouvé — entraînement en cours...")
    recommender.train(df_all)
    print("Modèle entraîné et sauvegardé !")
else:
    print("Modèle chargé — prêt à l'emploi !")

def get_categories(df: pd.DataFrame) -> list:
    col = "categorie" if "categorie" in df.columns else "produit_acheté"
    return sorted(df[col].dropna().unique().tolist())


def get_delegations(df: pd.DataFrame) -> list:
    return sorted(df["délégation"].dropna().unique().tolist())


def get_basket_analysis(
    df: pd.DataFrame,
    categorie: str = None,
    delegation: str = None,
    top_n: int = 5,
) -> list:
    """
    Retourne les top_n paires de produits les plus fréquemment
    achetées ensemble, avec filtres optionnels.
    """
    df_f = df.copy()
    df_f["date_dachat"] = pd.to_datetime(df_f["date_dachat"], errors="coerce")

    if categorie:
        if "categorie" in df_f.columns:
            df_f = df_f[df_f["categorie"] == categorie]

    if delegation:
        df_f = df_f[df_f["délégation"] == delegation]

    if df_f.empty:
        return []


    df_f["transaction"] = (
        df_f["client_id"].astype(str)
        + "_"
        + df_f["date_dachat"].dt.strftime("%Y-%m-%d")
    )

    transactions = df_f.groupby("transaction")["nom_produit"].apply(list)
    pair_counts = Counter()

    for items in transactions:
        unique_items = list({str(i).strip() for i in items if pd.notna(i)})
        if len(unique_items) >= 2:
            pair_counts.update(combinations(sorted(unique_items), 2))

    top_pairs = pair_counts.most_common(top_n)
    return [{"produits": list(pair), "frequence": count} for pair, count in top_pairs]


def get_cooccurrence_analysis(df: pd.DataFrame, produits: list, min_confidence: float = 5) -> dict:
    """
    Analyse la co-occurrence entre exactement deux produits.
    Délègue au modèle entraîné pour garantir la cohérence.
    """
    produits = [p.strip() for p in produits if p and p.strip()]

    if len(produits) != 2:
        return {
            "error": "Veuillez fournir exactement deux produits à analyser",
            "produits": produits,
        }

    if not recommender.product_names:
        return {
            "produit1": produits[0],
            "produit2": produits[1],
            "error": "Modèle non disponible. Veuillez réessayer.",
            "confidence": 0,
            "frequence_ensemble": 0,
            "frequence_produit1": 0,
            "frequence_produit2": 0,
            "sont_souvent_ensemble": False,
            "recommandation": "Modèle non disponible.",
            "details": {},
        }

    return recommender.analyze_pair(produits[0], produits[1])


# ──────────────────────────────────────────────────────────────────────────────
# NOUVELLE FONCTION : Suggestions de placement automatiques
# ──────────────────────────────────────────────────────────────────────────────

def get_placement_recommendations(df: pd.DataFrame, categorie: str = None, delegation: str = None, top_n: int = 10) -> dict:
    """
    Suggère automatiquement les placements de produits :
    - Produits à ÉLOIGNER (souvent achetés ensemble - cross-selling)
    - Produits à RAPPROCHER (rarement achetés ensemble)
    """
    df_f = df.copy()
    df_f["date_dachat"] = pd.to_datetime(df_f["date_dachat"], errors="coerce")
    
    if categorie and "categorie" in df_f.columns:
        df_f = df_f[df_f["categorie"] == categorie]
    
    if delegation and "délégation" in df_f.columns:
        df_f = df_f[df_f["délégation"] == delegation]
    
    if df_f.empty or not recommender.product_names:
        return {"error": "Données insuffisantes", "a_eloigner": [], "a_rapprocher": []}
    
    # Recalculer la clé de transaction sur le filtre
    df_f["transaction"] = (
        df_f["client_id"].astype(str)
        + "_"
        + df_f["date_dachat"].dt.strftime("%Y-%m-%d")
    )
    
    # Analyser TOUTES les paires du modèle pour ce filtre
    transactions = df_f.groupby("transaction")["nom_produit"].apply(list)
    
    # Recalculer les fréquences sur le filtre
    pair_counts = Counter()
    product_support_filtered = Counter()
    
    for items in transactions:
        unique_items = list({str(i).strip() for i in items if pd.notna(i)})
        for item in unique_items:
            product_support_filtered[item] += 1
        if len(unique_items) >= 2:
            for combo in combinations(sorted(unique_items), 2):
                pair_counts[combo] += 1
    
    total_trans_filtered = len(transactions)
    
    if total_trans_filtered == 0:
        return {"error": "Aucune transaction trouvée", "a_eloigner": [], "a_rapprocher": []}
    
    # Calculer les scores pour chaque paire
    recommendations = {
        "a_eloigner": [],    # lift > 1.5 et confiance > 10% (souvent ensemble → ÉLOIGNER)
        "a_rapprocher": [],  # lift < 0.8 (rarement ensemble → RAPPROCHER)
        "neutres": []
    }
    
    for (p1, p2), freq in pair_counts.items():
        freq1 = product_support_filtered[p1]
        freq2 = product_support_filtered[p2]
        
        if freq1 == 0 or freq2 == 0:
            continue
            
        conf = (freq / freq1) * 100
        expected = (freq1 * freq2) / total_trans_filtered if total_trans_filtered > 0 else 0
        lift = freq / expected if expected > 0 else 0
        
        # Score composite
        if lift >= 1:
            score = conf * lift * np.log1p(freq)
        else:
            score = conf * lift
        
        pair_info = {
            "produit1": p1,
            "produit2": p2,
            "lift": round(lift, 2),
            "confiance": round(conf, 1),
            "frequence_ensemble": freq,
            "score": round(score, 2)
        }
        
        # Classification pour placement (CORRIGÉE)
        if lift >= 1.5 and conf >= 10:
            # Souvent achetés ensemble → ÉLOIGNER pour maximiser le cross-selling
            recommendations["a_eloigner"].append(pair_info)
        elif lift < 0.8 or (lift < 1 and conf < 5):
            # Rarement achetés ensemble → RAPPROCHER (pas de risque)
            recommendations["a_rapprocher"].append(pair_info)
        else:
            recommendations["neutres"].append(pair_info)
    
    # Trier par pertinence
    recommendations["a_eloigner"].sort(key=lambda x: x["lift"], reverse=True)  # Les plus forts lift en premier
    recommendations["a_rapprocher"].sort(key=lambda x: x["lift"])  # Les plus faibles lift en premier
    
    return {
        "categorie_filtree": categorie,
        "delegation_filtree": delegation,
        "total_paires_analysees": len(pair_counts),
        "a_eloigner": recommendations["a_eloigner"][:top_n],      # ÉLOIGNER = souvent ensemble
        "a_rapprocher": recommendations["a_rapprocher"][:top_n],  # RAPPROCHER = rarement ensemble
        "conseils_generaux": _generer_conseils_placement(recommendations, top_n)
    }


def _generer_conseils_placement(recommendations: dict, top_n: int) -> list:
    """Génère des conseils de placement lisibles (CORRIGÉ)"""
    conseils = []
    
    if recommendations["a_eloigner"]:
        top_eloigner = recommendations["a_eloigner"][:3]
        produits_str = ", ".join([f"{p['produit1']} + {p['produit2']}" for p in top_eloigner])
        conseils.append({
            "type": "eloignement",
            "message": f"⚠️ À ÉLOIGNER : {produits_str}",
            "detail": "Ces produits sont très souvent achetés ensemble → éloignez-les pour maximiser le cross-selling"
        })
    
    if recommendations["a_rapprocher"]:
        top_rapprocher = recommendations["a_rapprocher"][:3]
        produits_str = ", ".join([f"{p['produit1']} + {p['produit2']}" for p in top_rapprocher])
        conseils.append({
            "type": "rapprochement",
            "message": f"✅ À RAPPROCHER : {produits_str}",
            "detail": "Ces produits sont rarement achetés ensemble → vous pouvez les placer côte à côte"
        })
    
    return conseils