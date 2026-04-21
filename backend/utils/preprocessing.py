import pandas as pd
from prophet import Prophet
from mlxtend.frequent_patterns import apriori, association_rules


# =========================
# LOAD DATA
# =========================
def load_data():
    df = pd.read_csv(
        "C:/Users/mariem/Documents/smart-sales-analytics/backend/data/ACHAT_NETTOYE_V2.csv",
        sep=";",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )

    # normalize columns
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
    df_raw = load_data()

    print("RAW CA:", pd.to_numeric(df_raw["prix_total"], errors="coerce").sum())
    print("RAW ROWS:", len(df_raw))

    df = df_raw.copy()

    # =========================
    # 1. TYPES
    # =========================
    df["prix_total"] = pd.to_numeric(df["prix_total"], errors="coerce")
    df["quantité_achetée"] = pd.to_numeric(df["quantité_achetée"], errors="coerce")
    df["prix_unitaire"] = pd.to_numeric(df["prix_unitaire"], errors="coerce")

    # =========================
    # 2. KEEP ONLY REAL FACT ROWS
    # =========================
    df = df.dropna(subset=[
        "prix_total",
        "client_id",
        "date_dachat"
    ])

    # =========================
    # 3. BUSINESS FILTERS (MINIMAL ONLY)
    # =========================

    # remove negative prices only
    df = df[df["prix_total"] > 0]

    # optional safety only (NOT strict)
    df = df[df["quantité_achetée"].notna()]

    # =========================
    # 4. DATE CLEANING
    # =========================
    df["date_dachat"] = pd.to_datetime(df["date_dachat"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date_dachat"])

    # =========================
    # 5. TEXT NORMALIZATION
    # =========================
    df["nom_produit"] = df["nom_produit"].fillna("unknown").astype(str).str.strip().str.lower()
    df["marque"] = df["marque"].fillna("unknown").astype(str).str.strip().str.lower()
    df["categorie"] = df["categorie"].fillna("unknown").astype(str).str.strip().str.lower()

    df["client_id"] = df["client_id"].astype(str).str.strip()

    # =========================
    # 6. DUPLICATES (LIGHT ONLY)
    # =========================
    df = df.drop_duplicates(subset=[
        "client_id",
        "date_dachat",
        "nom_produit",
        "prix_total",
        "quantité_achetée"
    ])

    # =========================
    # FINAL DEBUG
    # =========================
    print("FINAL CA:", df["prix_total"].sum())
    print("NB PRODUITS:", df["nom_produit"].nunique())
    print("NB MARQUES:", df["marque"].nunique())

    return df

df_cached = build_powerbi_model()


def get_clean_df():
    return df_cached.copy()


# =========================
# FORECAST PREP
# =========================
def preprocess_forecast():
    df = get_clean_df().copy()

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = df.groupby(
        pd.Grouper(key="date_dachat", freq="MS")
    )["prix_total"].sum().reset_index()

    df_month = df_month.rename(columns={
        "date_dachat": "ds",
        "prix_total": "y"
    })

    return df_month


# =========================
# CUSTOMER PREP
# =========================
def preprocess_customer():
    df = get_clean_df()

    client = df.groupby("client_id").agg({
        "prix_total": "sum",
        "quantité_achetée": "sum"
    }).reset_index()

    client["Panier_Moyen"] = client["prix_total"] / client["quantité_achetée"]
    client["HighValue"] = (client["prix_total"] > client["prix_total"].median()).astype(int)

    return client


# =========================
# ASSOCIATION RULES
# =========================
def get_association_rules():
    df = get_clean_df()

    basket = df.pivot_table(
        index="client_id",
        columns="nom_produit",
        values="quantité_achetée",
        aggfunc="sum",
        fill_value=0
    )

    basket = basket.iloc[:1000, :30]
    basket = basket > 0

    frequent = apriori(basket, min_support=0.02, use_colnames=True)

    if frequent.empty:
        return []

    rules = association_rules(frequent, metric="lift", min_threshold=1)

    if rules.empty:
        return []

    return rules.head(10).to_dict(orient="records")


# =========================
# FORECAST PRODUCT
# =========================
def forecast_by_product(product_name):
    df = get_clean_df()

    df = df[df["nom_produit"].str.lower() == product_name.lower()]

    if df.empty:
        return {"error": "Produit non trouvé"}

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = df.groupby(
        pd.Grouper(key="date_dachat", freq="MS")
    )["quantité_achetée"].sum().reset_index()

    df_month = df_month.rename(columns={"date_dachat": "ds", "quantité_achetée": "y"})

    model = Prophet()
    model.fit(df_month)

    future = model.make_future_dataframe(periods=3, freq="MS")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat"]].tail(3)

    max_value = result["yhat"].max() if result["yhat"].max() > 0 else 1
    result["probability"] = (result["yhat"] / max_value * 100).round(1)

    result["ds"] = result["ds"].dt.strftime("%B %Y")

    return result[["ds", "probability"]].to_dict(orient="records")