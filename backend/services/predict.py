from models.customer_model import predict_customer
from utils.preprocessing import preprocess_forecast, get_clean_df
from models.prediction_model import predict_future
from models.xgboost_forecast import predict_future_xgb
import pandas as pd


def get_sales_forecast(periods=6):

    df_month = preprocess_forecast()

    result = predict_future_xgb(df_month, periods=periods)

    return result


def forecast_by_product(product_name, periods=3, force_retrain=False):

    df = get_clean_df()

    df = df[df["nom_produit"].str.lower().str.contains(product_name.lower(), na=False)]

    if df.empty:
        return {"error": "Produit non trouvé"}

    df["date_dachat"] = pd.to_datetime(df["date_dachat"])

    df_month = (
        df.groupby(pd.Grouper(key="date_dachat", freq="MS"))["ca_calc"]
        .sum()
        .reset_index()
        .rename(columns={"date_dachat": "ds", "ca_calc": "y"})
    )

    if len(df_month) < 3:
        return {"error": "Pas assez de données"}

    return predict_future_xgb(df_month, periods=periods)

def get_customer_prediction(total, qty):
    return predict_customer(total, qty)