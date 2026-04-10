from utils.preprocessing import load_data
from itertools import combinations
from collections import Counter
import pandas as pd
from models import BasketRecommender

# Charger les données
df_all = load_data()
df_all["date_dachat"] = pd.to_datetime(df_all["date_dachat"], errors="coerce")
df_all["transaction"] = df_all["client_id"].astype(str) + "_" + df_all["date_dachat"].astype(str)

# Initialiser le modèle de recommandation (définir la variable recommender)
recommender = BasketRecommender(model_path="models/basket_model.pkl")

# Essayer de charger un modèle existant
print("Tentative de chargement du modèle existant...")
if not recommender.load_model():
    print("Aucun modèle trouvé. Entraînement du modèle...")
    recommender.train(df_all)
    print("Modèle entraîné et sauvegardé avec succès!")
else:
    print("Modèle chargé avec succès, prêt à l'emploi!")

def get_categories(df):
    return sorted(df["categorie"].dropna().unique().tolist())

def get_delegations(df):
    return sorted(df["délégation"].dropna().unique().tolist())

def get_basket_analysis(df, categorie=None, delegation=None, top_n=5):
    df_filtered = df.copy()
    if categorie and categorie != "":
        df_filtered = df_filtered[df_filtered["categorie"] == categorie]
    if delegation and delegation != "":
        df_filtered = df_filtered[df_filtered["délégation"] == delegation]
    
    if len(df_filtered) == 0:
        return []
    
    transactions = df_filtered.groupby("transaction")["nom_produit"].apply(list)
    pair_counts = Counter()
    
    for items in transactions:
        unique_items = [str(i) for i in set(items) if pd.notna(i)]
        if len(unique_items) >= 2:
            pair_counts.update(combinations(sorted(unique_items), 2))
    
    top_pairs = pair_counts.most_common(top_n)
    return [{"produits": list(pair), "frequence": count} for pair, count in top_pairs]

def get_cooccurrence_analysis(df, produits, min_confidence=5):
    """
    Analyse la co-occurrence entre deux produits
    Retourne un pourcentage de confiance et une recommandation de placement
    """
    # Nettoyer les produits
    produits = [p.strip() for p in produits if p and p.strip()]
    
    if len(produits) != 2:
        return {
            "error": "Veuillez fournir exactement deux produits à analyser",
            "produits": produits
        }
    
    produit1, produit2 = produits[0], produits[1]
    
    # Utiliser le modèle pour trouver les correspondances
    result = {
        "produit1": produit1,
        "produit2": produit2,
        "confidence": 0,
        "frequence_ensemble": 0,
        "frequence_produit1": 0,
        "frequence_produit2": 0,
        "sont_souvent_ensemble": False,
        "recommandation": "",
        "details": {}
    }
    
    # Vérifier que le modèle est disponible
    if not recommender.product_names:
        result["recommandation"] = "Modèle non disponible. Veuillez réessayer."
        result["error"] = "Model not available"
        return result
    
    # 1. Trouver les correspondances exactes
    product1_match = None
    product2_match = None
    
    for p in recommender.product_names:
        if p.lower() == produit1.lower():
            product1_match = p
        if p.lower() == produit2.lower():
            product2_match = p
    
    # 2. Si pas de correspondance exacte, chercher des produits similaires
    if not product1_match:
        similar1 = recommender.find_similar_products(produit1, top_n=1, threshold=0.3)
        if similar1:
            product1_match = similar1[0]['produit']
            result['details']['product1_matched'] = similar1[0]
    
    if not product2_match:
        similar2 = recommender.find_similar_products(produit2, top_n=1, threshold=0.3)
        if similar2:
            product2_match = similar2[0]['produit']
            result['details']['product2_matched'] = similar2[0]
    
    if not product1_match or not product2_match:
        result["recommandation"] = "Impossible d'analyser: un ou plusieurs produits non trouvés"
        result["details"]["missing"] = []
        if not product1_match:
            result["details"]["missing"].append(produit1)
        if not product2_match:
            result["details"]["missing"].append(produit2)
        return result
    
    # 3. Calculer les fréquences
    result["produit1"] = product1_match
    result["produit2"] = product2_match
    result["frequence_produit1"] = recommender.product_support.get(product1_match, 0)
    result["frequence_produit2"] = recommender.product_support.get(product2_match, 0)
    
    # 4. Trouver la fréquence d'achat ensemble
    pair_key = tuple(sorted([product1_match, product2_match]))
    freq_ensemble = recommender.pair_frequencies.get(pair_key, 0)
    result["frequence_ensemble"] = freq_ensemble
    
    # 5. Calculer la confiance
    if result["frequence_produit1"] > 0:
        confidence = (freq_ensemble / result["frequence_produit1"]) * 100
        result["confidence"] = round(confidence, 1)
    
    # 6. Déterminer la recommandation
    if result["confidence"] >= 30:
        result["sont_souvent_ensemble"] = True
        result["recommandation"] = f"⚠️ ATTENTION: Ces produits sont souvent achetés ensemble ({result['confidence']}% de confiance). Il est recommandé de les placer à des emplacements éloignés pour maximiser les ventes croisées."
        result["details"]["conseil"] = "Placer ces produits dans des rayons différents pour encourager la découverte"
    elif result["confidence"] >= 15:
        result["sont_souvent_ensemble"] = True
        result["recommandation"] = f"⚠️ Ces produits sont modérément achetés ensemble ({result['confidence']}% de confiance). On peut les placer à distance modérée."
        result["details"]["conseil"] = "Peuvent être placés dans des rayons proches mais pas côte à côte"
    elif result["confidence"] >= 5:
        result["sont_souvent_ensemble"] = False
        result["recommandation"] = f"ℹ️ Ces produits sont parfois achetés ensemble ({result['confidence']}% de confiance). Le placement n'a pas d'impact majeur."
        result["details"]["conseil"] = "Placement libre, pas de contrainte particulière"
    elif result["confidence"] > 0:
        result["sont_souvent_ensemble"] = False
        result["recommandation"] = f"✅ Ces produits sont rarement achetés ensemble ({result['confidence']}% de confiance). Ils peuvent être placés à proximité sans problème."
        result["details"]["conseil"] = "Peuvent être placés côte à côte"
    else:
        result["sont_souvent_ensemble"] = False
        result["recommandation"] = "✅ Ces produits ne sont jamais achetés ensemble. Ils peuvent être placés à proximité sans risque."
        result["details"]["conseil"] = "Placement libre, aucun impact sur les ventes"
    
    # 7. Ajouter des informations supplémentaires
    result["details"]["interpretation"] = {
        "frequence_ensemble": freq_ensemble,
        "total_transactions_avec_produit1": result["frequence_produit1"],
        "total_transactions_avec_produit2": result["frequence_produit2"],
        "confidence_percent": result["confidence"]
    }
    
    return result