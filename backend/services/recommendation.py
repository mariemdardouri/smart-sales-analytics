from utils.preprocessing import load_data
from services.analytics import forecast_by_product

def recommend_stock():
    df = load_data()

    products = df["nom_produit"].unique()

    recommendations = []

    for product in products[:20]: 
        try:
            forecast = forecast_by_product(product)
            predicted = forecast[-1]["yhat"]

            current_stock = df[df["nom_produit"] == product]["quantité_achetée"].mean()

            if predicted > current_stock:
                recommendations.append({
                    "produit": product,
                    "predicted_demand": float(predicted),
                    "current_stock": float(current_stock),
                    "action": "BUY MORE"
                })
        except:
            continue

    return recommendations