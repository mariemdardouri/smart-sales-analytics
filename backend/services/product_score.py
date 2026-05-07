

from utils.preprocessing import load_data

def product_score():
    df = load_data()

    grouped = df.groupby("nom_produit").agg({
        "quantité_achetée": "sum",
        "prix_total": "sum",
        "date_dachat": "count"
    }).reset_index()

    grouped.columns = ["produit", "volume", "revenue", "frequency"]


    grouped["score"] = (
        grouped["volume"] * 0.5 +
        grouped["revenue"] * 0.3 +
        grouped["frequency"] * 0.2
    )

    top = grouped.sort_values(by="score", ascending=False).head(10)

    return top.to_dict(orient="records")