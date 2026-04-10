from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from services.predict import get_sales_forecast, get_customer_prediction
from models.segmentation import get_clusters
from utils.preprocessing import preprocess_forecast
from utils.preprocessing import forecast_by_product
from services.basket_service import df_all, get_categories, get_delegations, get_basket_analysis, get_cooccurrence_analysis
import pandas as pd
from typing import List
from pydantic import BaseModel
from services.chat_service import ask_chatbot
app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, etc.
    allow_headers=["*"],         # tous les headers
)
"""
@app.get("/")
def home():
    return {"message": "API running"}

@app.get("/forecast")
def forecast():
    return get_sales_forecast()

@app.get("/predict-customer")
def predict(total: float, qty: int):
    return {"prediction": get_customer_prediction(total, qty)}

@app.get("/segmentation")
def segmentation():
    return get_clusters()

@app.get("/sales/total")
def sales_total():
    df = preprocess_forecast()
    total = df["prix_total"].sum()
    return {"total_sales": total}
"""

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    answer = ask_chatbot(request.question)
    return {"answer": answer}




class ProductPairRequest(BaseModel):
    produits: List[str]

@app.get("/categories")
def categories_endpoint():
    return get_categories(df_all)

@app.get("/delegations")
def delegations_endpoint():
    return get_delegations(df_all)

@app.get("/basket")
def basket_endpoint(categorie: str = None, delegation: str = None, top_n: int = 5):
    return get_basket_analysis(df_all, categorie, delegation, top_n)

@app.post("/analyze-pair")
def analyze_pair_endpoint(request: ProductPairRequest):
    """
    Analyse si deux produits sont souvent achetés ensemble
    Attend: {"produits": ["produit1", "produit2"]}
    Retourne: Pourcentage de confiance et recommandation de placement
    """
    return get_cooccurrence_analysis(df_all, request.produits)

@app.get("/forecast/product")
def forecast_product(name: str):
    return forecast_by_product(name)