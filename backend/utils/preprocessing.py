import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def load_data():
    df = pd.read_csv(
        "data/ACHAT_NETTOYE_V2.csv",
        sep=";",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("ã©", "e")
        .str.replace("'", "")
    )

    print(df.columns)

    return df

def preprocess_forecast():

    df = load_data()

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = df.groupby(
        pd.Grouper(key="date_dachat", freq="ME")
    )["prix_total"].sum().reset_index()

    df_month = df_month.rename(columns={
        "date_dachat": "ds",
        "prix_total": "y"
    })

    return df_month


def preprocess_customer():

    df = load_data()

    client = df.groupby("client_id").agg({
        "prix_total": "sum",
        "quantité_achetée": "sum"
    }).reset_index()

    client["Panier_Moyen"] = client["prix_total"] / client["quantité_achetée"]

    client["HighValue"] = (client["prix_total"] > client["prix_total"].median()).astype(int)

    return client

def get_association_rules():
    df = load_data()

    basket = df.groupby(
        ["date_dachat", "nom_produit"]
    )["quantité_achetée"].sum().unstack().fillna(0)

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)

    frequent = apriori(basket, min_support=0.02, use_colnames=True)

    rules = association_rules(frequent, metric="lift", min_threshold=1)

    return rules[["antecedents", "consequents", "support", "confidence"]].head(10).to_dict(orient="records")

def forecast_by_product(product_name):
    df = load_data()

    df = df[df["nom_produit"] == product_name]

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df = df.groupby("date_dachat")["quantité_achetée"].sum().reset_index()

    df = df.rename(columns={
        "date_dachat": "ds",
        "quantité_achetée": "y"
    })

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=3, freq="M")
    forecast = model.predict(future)

    return forecast[["ds", "yhat"]].tail(3).to_dict(orient="records")