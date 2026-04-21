from models.customer_model import predict_customer
from utils.preprocessing import preprocess_forecast
from prophet import Prophet

def get_sales_forecast():
    df = preprocess_forecast()

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=3, freq="ME")
    forecast = model.predict(future)

    return forecast[["ds", "yhat"]].tail(6).to_dict(orient="records")

def get_customer_prediction(total, qty):
    return predict_customer(total, qty)