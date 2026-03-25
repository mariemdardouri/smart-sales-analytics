from fastapi import FastAPI
from models.segmentation import get_clusters
from services import product_score
from services.assisstant import business_assistant
from services.bundle import get_product_bundles
from services.geo_analysis import geo_analysis
from services.recommendation import recommend_stock
from services.analytics import get_products_by_client
from services.analytics import get_association_rules
from utils.preprocessing import forecast_by_product, preprocess_forecast
from services.predict import get_sales_forecast, get_customer_prediction
from services.analytics import get_top_products, get_customer_products, get_association_rules, forecast_by_product

app = FastAPI()

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

@app.get("/products/top")
def top_products():
    return get_top_products()

@app.get("/products/customer/{id}")
def customer_products(id: int):
    return get_customer_products(id)

@app.get("/products/association")
def association():
    return get_association_rules()

@app.get("/forecast/product")
def forecast_product(name: str):
    return forecast_by_product(name)

@app.get("/recommend/stock")
def stock():
    return recommend_stock()

@app.get("/recommend/bundles")
def bundles():
    return get_product_bundles()
@app.get("/products/score")
def score():
    return product_score()
@app.get("/assistant/business")
def assistant():
    return business_assistant()
@app.get("/analysis/geo")
def geo():
    return geo_analysis()

@app.get("/association")
def association():
    return get_association_rules()

@app.get("/products/client")
def products_client(client_id: int):
    return get_products_by_client(client_id)