from utils.preprocessing import load_data
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from prophet import Prophet

def get_top_products(n=10):
    df = load_data()

    top = df.groupby("nom_produit")["quantité_achetée"] \
            .sum() \
            .sort_values(ascending=False) \
            .head(n)

    return top.reset_index().to_dict(orient="records")


def get_customer_products(client_id):
    df = load_data()

    client_df = df[df["client_id"] == client_id]

    products = client_df.groupby("nom_produit")["quantité_achetée"] \
                        .sum() \
                        .sort_values(ascending=False)

    return products.reset_index().to_dict(orient="records")

def get_association_rules():
    df = load_data()

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    basket = df.groupby(
        ["date_dachat", "nom_produit"]
    )["quantité_achetée"].sum().unstack().fillna(0)

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)

    frequent = apriori(basket, min_support=0.02, use_colnames=True)

    rules = association_rules(frequent, metric="lift", min_threshold=1)

    return rules[["antecedents", "consequents", "support", "confidence"]] \
        .head(10).to_dict(orient="records")


def forecast_by_product(name):
    df = load_data()

    df = df[df["nom_produit"] == name]

    df = df.groupby("date_dachat")["quantité_achetée"].sum().reset_index()
    df.columns = ["ds", "y"]

    if len(df) < 2:
        return {"error": "Pas assez de données pour ce produit"}

    from prophet import Prophet

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=3, freq="ME")

    forecast = model.predict(future)

    return forecast[["ds", "yhat"]].tail(3).to_dict(orient="records")

def get_association_rules():
    df = load_data()

    basket = df.groupby(['client_id', 'nom_produit'])['quantité_achetée'] \
               .sum().unstack().fillna(0)

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)

    frequent = apriori(basket, min_support=0.02, use_colnames=True)
    rules = association_rules(frequent, metric="lift", min_threshold=1)

    return rules[['antecedents', 'consequents']].astype(str).to_dict(orient="records")
import pandas as pd

def get_products_by_client(client_id):
    df = load_data()

    client_data = df[df['client_id'] == client_id]

    data = client_data.to_dict(orient='records')
    for row in data:
        for k, v in row.items():
            if pd.isna(v):
                row[k] = None

    return {"products": data}