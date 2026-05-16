from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from typing import List,Optional
from pydantic import BaseModel
import models.xgboost_forecast as xgb_model
from models.prediction_model import predict_future

from services.predict import get_sales_forecast, get_customer_prediction,forecast_by_product
from models.segmentation import get_clusters

from utils.preprocessing import (
    get_association_rules,
    get_dim_produit,
    preprocess_forecast,
    get_clean_df
)

from services.basket_service import (
    df_all,
    get_categories,
    get_delegations,
    get_basket_analysis,
    get_cooccurrence_analysis,
    get_placement_recommendations
)

from services.sales_service import (
    get_available_categories, 
    get_available_delegations,
    get_available_localites,
    predict_sales,
    get_model_metrics,
    get_feature_importance
)


from services.location_service import (
    get_available_categories as loc_get_categories,
    get_all_regions,
    get_best_region,
    get_model_metrics as loc_get_model_metrics
)
from auth_routes import router as auth_router



app = FastAPI(title="Smart Sales Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

def df():
    return get_clean_df()


@app.get("/")
def home():
    return {"message": "API running successfully"}


@app.get("/forecast")
def forecast(periods: int = 6):
    return get_sales_forecast(periods)

@app.get("/forecast/product")
def forecast_product(name: str, periods: int = 3, force_retrain: bool = False):
    return forecast_by_product(name, periods, force_retrain)
@app.get("/forecast/product-prophet")
def prophet_product(name: str, periods: int = 3):

    df = get_clean_df()

    df = df[df["nom_produit"].str.lower().str.contains(name.lower(), na=False)]

    if df.empty:
        return {"error": "Produit non trouvé"}

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = (
        df.groupby(pd.Grouper(key="date_dachat", freq="MS"))["ca_calc"]
        .sum()
        .reset_index()
        .rename(columns={"date_dachat": "ds", "ca_calc": "y"})
    )

    return predict_future(df_month, df_key=f"prophet_{name}", periods=periods)

@app.get("/forecast/product-xgb")
def xgb_product(name: str, periods: int = 3):
    df = get_clean_df()
    df = df[df["nom_produit"].str.lower() == name.lower()]

    if df.empty:
        return {"error": "Produit non trouvé"}

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = (
        df.groupby(pd.Grouper(key="date_dachat", freq="MS"))["ca_calc"]
        .sum()
        .reset_index()
        .rename(columns={"date_dachat": "ds", "ca_calc": "y"})
    )

    return xgb_model.predict_future_xgb(df_month, periods=periods)

@app.get("/products/names")
def product_names(q: str = ""):
    dff = df()
    names = dff["nom_produit"].dropna().unique().tolist()
    if q:
        names = [n for n in names if q.lower() in n.lower()]
    return sorted(names)[:20]
 


@app.get("/predict-customer")
def predict(total: float, qty: int):
    return {"prediction": get_customer_prediction(total, qty)}


@app.get("/segmentation")
def segmentation():
    return get_clusters()


@app.get("/sales/total")
def sales_total():
    dff = preprocess_forecast()
    return {"total_sales": float(dff["y"].sum())}

class ProductPairRequest(BaseModel):
    produits: List[str]


class ChatRequest(BaseModel):
    question: str

@app.get("/categories")
def categories_endpoint():
    return get_categories(df())


@app.get("/delegations")
def delegations_endpoint():
    return get_delegations(df())


@app.get("/basket")
def basket_endpoint(categorie: str = None, delegation: str = None, top_n: int = 5):
    return get_basket_analysis(df(), categorie, delegation, top_n)


@app.post("/analyze-pair")
def analyze_pair_endpoint(request: ProductPairRequest):
    return get_cooccurrence_analysis(df(), request.produits)


@app.get("/products/top")
def top_products():
    dff = df()
    top = dff["nom_produit"].value_counts().head(5)

    return [
        {"nom_produit": k, "quantité_achetée": int(v)}
        for k, v in top.items()
    ]

try:
    from services.chat_service import ask_chatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    if not CHATBOT_AVAILABLE:
        return {"answer": "Chatbot non disponible"}
    return {"answer": ask_chatbot(request.question)}

cached_rules = get_association_rules()


@app.get("/association")
def association():
    return cached_rules

@app.get("/analytics/produit/kpi")
def produit_kpi():
    dff = df()
    dim = get_dim_produit()
    return {
        "ca_total":    round(float(dff["ca_calc"].sum()), 2),  
        "nb_produits": int(dim["nom_produit"].nunique()),      
        "nb_marques":  int(dim["marque"].nunique())           
    }

@app.get("/analytics/produit/ca-produit")
def ca_produit():
    dff = df()
    data = dff.groupby("nom_produit")["ca_calc"].sum().sort_values(ascending=False).head(10)
    return {"labels": data.index.tolist(), "values": data.values.tolist()}


@app.get("/analytics/produit/ca-categorie")
def ca_categorie():
    dff = df()
    return dff.groupby("categorie")["ca_calc"].sum().to_dict()


@app.get("/analytics/produit/prix-moyen-categorie")
def prix_moyen():
    dff = df()
    return dff.groupby("categorie")["ca_calc"].mean().to_dict()

@app.get("/analytics/produit/ca-marque")
def ca_marque():
    dff = df()
    data = dff.groupby("marque")["ca_calc"].sum()
    return {"labels": data.index.tolist(), "values": data.values.tolist()}


@app.get("/analytics/temps/kpi")
def temps_kpi():
    dff = df()
    return {
        "ca_total":        round(float(dff["ca_calc"].sum()), 2),
        "nb_transactions": int(len(dff)),
        "panier_moyen":    round(float(dff["ca_calc"].mean()), 2) 
    }


@app.get("/analytics/temps/trimestre")
def ca_trimestre():
    dff = df()
    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])
    dff["trimestre"] = dff["date_dachat"].dt.quarter
    return dff.groupby("trimestre")["ca_calc"].sum().to_dict()


@app.get("/analytics/temps/mois")
def ca_mois():
    dff = df()
    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])
    data = dff.groupby(dff["date_dachat"].dt.to_period("M"))["ca_calc"].sum()
    return {"labels": data.index.astype(str).tolist(), "values": data.values.tolist()}

@app.get("/analytics/temps/saison")
def ca_saison():
    dff = df()
    def season(m):
        if m in [12,1,2]: return "Hiver"
        if m in [3,4,5]: return "Printemps"
        if m in [6,7,8]: return "Été"
        return "Automne"
    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])
    dff["saison"] = dff["date_dachat"].dt.month.apply(season)
    return dff.groupby("saison")["ca_calc"].sum().to_dict()

@app.get("/analytics/geo/kpi")
def geo_kpi():
    dff = df()

    return {
        "nb_clients": int(dff["client_id"].nunique()),
        "nb_localites": int(dff["localité"].nunique()),
        "nb_delegations": int(dff["délégation"].nunique())
    }


@app.get("/analytics/geo/ca-delegation")
def ca_delegation():
    dff = df().dropna(subset=["délégation"])
    data = dff.groupby("délégation")["ca_calc"].sum().sort_values(ascending=False).head(10)
    return data.to_dict()



@app.get("/analytics/geo/ca-localite")
def ca_localite():
    dff = df().dropna(subset=["localité"])
    data = dff.groupby("localité")["ca_calc"].sum().sort_values(ascending=False).head(10)
    return data.to_dict()

@app.get("/analytics/geo/clients-delegation")
def clients_delegation():
    dff = df()

    return (
        dff.groupby("délégation")["client_id"]
        .nunique()
        .to_dict()
    )



@app.get("/sales/categories")
async def sales_categories():
    return get_available_categories()

@app.get("/sales/delegations")
async def sales_delegations():
    return get_available_delegations()

@app.get("/sales/localites")
async def sales_localites(delegation: str = None):
    return get_available_localites(delegation)

@app.post("/sales/predict")
async def sales_predict(request: dict):

    categories = request.get("categories", [])
    delegation = request.get("delegation")
    localite = request.get("localite")
    month = request.get("month")

    if not categories:
        return {"error": "Veuillez spécifier au moins une catégorie"}

    return predict_sales(categories, delegation, localite, month)


@app.get("/sales/metrics")
async def sales_metrics():
    return get_model_metrics()

@app.get("/sales/feature-importance")
async def sales_feature_importance():
    return get_feature_importance()




class LocationRequest(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None
    top_n: int = 5


@app.get("/location/categories")
def location_categories():
    return loc_get_categories()


@app.get("/location/regions")
def location_regions():
    return get_all_regions()


@app.post("/location/predict")
def location_predict(request: LocationRequest):

    return get_best_region(
        category=request.category,
        brand=request.brand,
        product_name=request.product_name,
        top_n=request.top_n
    )


@app.get("/location/metrics")
def location_metrics():
    return loc_get_model_metrics()

@app.get("/placement/recommendations")
def placement_recommendations(categorie: str = None, delegation: str = None, top_n: int = 10):
    """Suggère automatiquement les placements de produits"""
    from services.basket_service import get_placement_recommendations
    return get_placement_recommendations(df(), categorie, delegation, top_n)

@app.get("/layout/recommendations")
async def layout_recommendations(delegation: str = None):
    """
    Retourne les recommandations de layout de magasin
    (quelles catégories rapprocher ou éloigner)
    """
    from services.basket_service import get_layout_by_delegation
    return get_layout_by_delegation(df(), delegation)
# ─────────────────────────────────────────────────────────────
# BASKET ANALYSIS ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/placement/recommendations")
def placement_recommendations(
    categorie: str = None,
    delegation: str = None,
    top_n: int = 10
):
    """
    Analyse des produits :
    - Produits à rapprocher
    - Produits à éloigner
    """

    return get_placement_recommendations(
        df(),
        categorie,
        delegation,
        top_n
    )


@app.get("/layout/recommendations")
def layout_recommendations(
    delegation: str = None
):
    """
    Analyse catégories :
    - catégories à rapprocher
    - catégories à éloigner
    """

    from services.basket_service import get_layout_by_delegation

    return get_layout_by_delegation(
        df(),
        delegation
    )