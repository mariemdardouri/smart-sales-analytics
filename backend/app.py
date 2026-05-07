from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from services.sales_service import (
    get_available_categories, 
    get_available_delegations,
    get_available_localites,
    predict_sales,
    get_model_metrics,
    get_feature_importance
)
from services.predict import get_customer_prediction
from models.segmentation import get_clusters

from utils.preprocessing import (
    get_association_rules,
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


from services.location_service import (
    get_available_categories as loc_get_categories,
    get_all_regions,
    get_best_region,
    get_model_metrics as loc_get_model_metrics
)

# APP INIT

app = FastAPI(title="Smart Sales Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SINGLE SOURCE OF TRUTH

def df():
    return get_clean_df()


# BASIC ROUTES

@app.get("/")
def home():
    return {"message": "API running successfully"}


@app.get("/predict-customer")
def predict(total: float, qty: int):
    return {"prediction": get_customer_prediction(total, qty)}


@app.get("/segmentation")
def segmentation():
    return get_clusters()



# MODELS

class ProductPairRequest(BaseModel):
    produits: List[str]


class ChatRequest(BaseModel):
    question: str



# BASKET

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


# CHAT

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



# ASSOCIATION RULES

cached_rules = get_association_rules()


@app.get("/association")
def association():
    return cached_rules



# PRODUIT ANALYTICS (UNCHANGED)

@app.get("/analytics/produit/kpi")
def produit_kpi():
    dff = df()

    return {
        "ca_total": round(
            dff.groupby(
                ["client_id", "nom_produit", "date_dachat"]
            )["prix_total"].sum().sum(),
            2
        ),
        "nb_produits": dff["nom_produit"].nunique(),
        "nb_marques": dff["marque"].nunique()
    }


@app.get("/analytics/produit/ca-produit")
def ca_produit():
    dff = df()

    data = (
        dff.groupby("nom_produit")["prix_total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    return {
        "labels": data.index.tolist(),
        "values": data.values.tolist()
    }


@app.get("/analytics/produit/ca-categorie")
def ca_categorie():
    dff = df()
    return dff.groupby("categorie")["prix_total"].sum().to_dict()


@app.get("/analytics/produit/prix-moyen-categorie")
def prix_moyen():
    dff = df()
    return dff.groupby("categorie")["prix_total"].mean().to_dict()


@app.get("/analytics/produit/ca-marque")
def ca_marque():
    dff = df()

    data = dff.groupby("marque")["prix_total"].sum()

    return {
        "labels": data.index.tolist(),
        "values": data.values.tolist()
    }



# TEMPS

@app.get("/analytics/temps/kpi")
def temps_kpi():
    dff = df()

    return {
        "ca_total": round(float(dff["prix_total"].sum()), 2),
        "nb_transactions": int(len(dff)),
        "panier_moyen": round(float(dff["prix_total"].mean()), 2)
    }


@app.get("/analytics/temps/trimestre")
def ca_trimestre():
    dff = df()
    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])
    dff["trimestre"] = dff["date_dachat"].dt.quarter

    return dff.groupby("trimestre")["prix_total"].sum().to_dict()


@app.get("/analytics/temps/mois")
def ca_mois():
    dff = df()

    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])

    data = (
        dff.groupby(dff["date_dachat"].dt.to_period("M"))["prix_total"]
        .sum()
    )

    return {
        "labels": data.index.astype(str).tolist(),
        "values": data.values.tolist()
    }


@app.get("/analytics/temps/saison")
def ca_saison():
    dff = df()

    def season(m):
        if m in [12, 1, 2]: return "Hiver"
        if m in [3, 4, 5]: return "Printemps"
        if m in [6, 7, 8]: return "Été"
        return "Automne"

    dff["date_dachat"] = pd.to_datetime(dff["date_dachat"])
    dff["saison"] = dff["date_dachat"].dt.month.apply(season)

    return dff.groupby("saison")["prix_total"].sum().to_dict()



# GEO

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
    dff = df()

    dff = dff.dropna(subset=["délégation"])

    data = (
        dff.groupby("délégation")["prix_total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    return data.to_dict()


@app.get("/analytics/geo/ca-localite")
def ca_localite():
    dff = df()

    dff = dff.dropna(subset=["localité"])

    data = (
        dff.groupby("localité")["prix_total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    return data.to_dict()


@app.get("/analytics/geo/clients-delegation")
def clients_delegation():
    dff = df()

    return (
        dff.groupby("délégation")["client_id"]
        .nunique()
        .to_dict()
    )


# SALES MODEL

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



# LOCATION 


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
@app.get("/placement/recommendations")
def placement_recommendations(categorie: str = None, delegation: str = None, top_n: int = 10):
    """Suggère automatiquement les placements de produits"""
    from services.basket_service import get_placement_recommendations
    return get_placement_recommendations(df(), categorie, delegation, top_n)