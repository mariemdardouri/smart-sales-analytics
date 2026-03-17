from fastapi import FastAPI
from services.predict import get_sales_forecast, get_customer_prediction
from models.segmentation import get_clusters

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