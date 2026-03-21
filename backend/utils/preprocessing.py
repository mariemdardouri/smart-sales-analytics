import pandas as pd

def load_data():
    df = pd.read_csv(
        "C:/Users/HP/Desktop/ACHAT_NETTOYE_final.csv",
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