from prophet import Prophet
from utils.preprocessing import preprocess_forecast

df = preprocess_forecast()

model = Prophet()
model.fit(df)

future = model.make_future_dataframe(periods=3, freq="ME")
forecast = model.predict(future)

def get_forecast():
    return forecast[["ds", "yhat"]].tail(6).to_dict(orient="records")