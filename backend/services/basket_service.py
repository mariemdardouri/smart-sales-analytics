from utils.preprocessing import load_data
from itertools import combinations
from collections import Counter
import pandas as pd
from models import BasketRecommender

# ──────────────────────────────────────────────────────────────────────────────
# Chargement des données
# ──────────────────────────────────────────────────────────────────────────────
df_all = load_data()

# Colonnes EXACTES confirmées par les logs :
#   client_id | délégation | localité | code_postal | date_dachat |
#   produit_acheté | quantité_achetée | prix_unitaire | prix_total |
#   année | mois | jour | produit_clean | nom_produit | marque |
#   taille_reference | categorie

df_all["date_dachat"] = pd.to_datetime(df_all["date_dachat"], errors="coerce")

# ── Clé de transaction ────────────────────────────────────────────────────────
# Tous les produits achetés par un même client le même jour = un panier
df_all["transaction"] = (
    df_all["client_id"].astype(str)
    + "_"
    + df_all["date_dachat"].dt.strftime("%Y-%m-%d")
)

# ──────────────────────────────────────────────────────────────────────────────
# Modèle de recommandation
# ──────────────────────────────────────────────────────────────────────────────
recommender = BasketRecommender(model_path="models/basket_model.pkl")

print("Tentative de chargement du modèle existant...")
if not recommender.load_model():
    print("Aucun modèle trouvé — entraînement en cours...")
    recommender.train(df_all)
    print("Modèle entraîné et sauvegardé !")
else:
    print("Modèle chargé — prêt à l'emploi !")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers exposés aux endpoints FastAPI
# ──────────────────────────────────────────────────────────────────────────────

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

    # Recalculer la clé de transaction sur le sous-ensemble filtré
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