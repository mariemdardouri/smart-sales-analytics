# services/assistant.py

from utils.preprocessing import load_data

def business_assistant():
    df = load_data()

    top_products = df.groupby("nom_produit")["quantité_achetée"] \
                    .sum().sort_values(ascending=False).head(10)

    avg_price = df["prix_total"].mean()

    categories = df["categorie"].value_counts().head(5)

    return {
        "message": "Voici les recommandations pour ouvrir une épicerie",
        "top_products": top_products.index.tolist(),
        "average_price": float(avg_price),
        "top_categories": categories.index.tolist()
    }