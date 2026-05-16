import pandas as pd
from prophet import Prophet
from mlxtend.frequent_patterns import apriori, association_rules


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
    return df


def build_powerbi_model():
    df = load_data()

    df["prix_total"]       = pd.to_numeric(df["prix_total"],       errors="coerce")
    df["quantité_achetée"] = pd.to_numeric(df["quantité_achetée"], errors="coerce")
    df["prix_unitaire"]    = pd.to_numeric(df["prix_unitaire"],     errors="coerce")

    df = df.dropna(subset=["prix_total", "client_id", "date_dachat"])
    df = df[df["prix_total"] > 0]
    df = df[df["quantité_achetée"].notna()]
    df = df[df["prix_unitaire"].notna()]
    df = df[df["prix_unitaire"] > 0]    

    df["date_dachat"] = pd.to_datetime(df["date_dachat"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date_dachat"])

    for col in ["nom_produit", "marque", "categorie"]:
        df[col] = df[col].astype(str).str.strip().str.lower()

    df["client_id"] = df["client_id"].astype(str).str.strip()


    NULLISH = {"nan", "none", "", "unknown", "inconnu", "n/a", "na"}
    for col in ["nom_produit", "marque", "categorie"]:
        df = df[~df[col].isin(NULLISH)]

    df = df.drop_duplicates(subset=[
        "client_id",
        "date_dachat",
        "produit_acheté",
        "prix_total",
        "quantité_achetée"
    ])

    df["ca_calc"] = df["quantité_achetée"] * df["prix_unitaire"]

    dim_produit = df.drop_duplicates(subset=["produit_acheté"])[
        ["produit_acheté", "nom_produit", "marque", "categorie"]
    ]

    valid_produits = dim_produit["produit_acheté"].unique()
    df = df[df["produit_acheté"].isin(valid_produits)]
    df["ca_calc"] = df["quantité_achetée"] * df["prix_unitaire"]

    print("✅ FINAL CA     :", round(df["ca_calc"].sum() / 1e6, 2), "M")
    print("✅ NB PRODUITS  :", dim_produit["nom_produit"].nunique())
    print("✅ NB MARQUES   :", dim_produit["marque"].nunique())

    return df, dim_produit  

df_cached, dim_produit_cached = build_powerbi_model()


def get_clean_df():
    return df_cached.copy()

def get_dim_produit():
    return dim_produit_cached.copy()

def preprocess_forecast(product_name=None):
    df = get_clean_df()
    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    if product_name:
        df = df[df["nom_produit"].str.lower() == product_name.lower()]

    df_month = (
        df.groupby(pd.Grouper(key="date_dachat", freq="MS"))["ca_calc"]
        .sum()
        .reset_index()
        .rename(columns={
            "date_dachat": "ds",
            "ca_calc": "y"
        })
    )

    return df_month

def preprocess_customer():
    df = get_clean_df()
    client = df.groupby("client_id").agg(
        prix_total=("prix_total", "sum"),
        quantité_achetée=("quantité_achetée", "sum")
    ).reset_index()
    client["Panier_Moyen"] = client["prix_total"] / client["quantité_achetée"]
    client["HighValue"]    = (client["prix_total"] > client["prix_total"].median()).astype(int)
    return client

def get_association_rules():
    df = get_clean_df()
    basket = df.pivot_table(
        index="client_id",
        columns="nom_produit",
        values="quantité_achetée",
        aggfunc="sum",
        fill_value=0
    )
    basket = basket.iloc[:1000, :30] > 0
    frequent = apriori(basket, min_support=0.02, use_colnames=True)
    if frequent.empty:
        return []
    rules = association_rules(frequent, metric="lift", min_threshold=1)
    if rules.empty:
        return []
    return rules.head(10).to_dict(orient="records")
