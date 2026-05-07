import pandas as pd
import numpy as np
import os
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_CACHE = {}
MODEL_META_CACHE = {}

def get_model(df_key, df):
    if df_key in MODEL_CACHE:
        return MODEL_CACHE[df_key]

    df_hash = hash(str(df.shape) + str(df["y"].sum()))

    if df_key in MODEL_META_CACHE:
        return MODEL_META_CACHE[df_key]

    model = SalesForecastModel()
    model.train(df)

    MODEL_CACHE[df_key] = model
    MODEL_META_CACHE[df_key] = model

    return model


# =========================
# MODEL CLASS
# =========================
class SalesForecastModel:

    def __init__(self):
        self.model = None
        self.metrics = {}

    # =========================
    # TRAIN
    # =========================
    def train(self, df):

        df = df.copy()
        df["ds"] = pd.to_datetime(df["ds"])
        df["y"] = df["y"].astype(float)

        # light smoothing (optional but safe)
        df["y"] = df["y"].rolling(3, min_periods=1).mean()

        train_size = int(len(df) * 0.8)
        df_train = df.iloc[:train_size]
        df_test = df.iloc[train_size:]

        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.1
        )

        self.model.add_seasonality(
            name="monthly",
            period=30.5,
            fourier_order=8
        )

        self.model.fit(df_train)

        # =========================
        # EVALUATION
        # =========================
        future = df_test[["ds"]]
        pred = self.model.predict(future)["yhat"].values
        y_true = df_test["y"].values

        self.metrics = {
            "MAE": float(mean_absolute_error(y_true, pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, pred))),
            "R2": float(r2_score(y_true, pred))
        }

        print("📊 MODEL METRICS:", self.metrics)

        return self

    # =========================
    # PREDICT
    # =========================
    def predict(self, df, periods=3):

        future = self.model.make_future_dataframe(periods=periods, freq="MS")
        forecast = self.model.predict(future)

        result = forecast[["ds", "yhat"]].tail(periods)

        return [
            {
                "ds": r["ds"].strftime("%Y-%m"),
                "yhat": float(max(0, r["yhat"]))
            }
            for _, r in result.iterrows()
        ]


# =========================
# ENTRY POINT (IMPORTANT FIX)
# =========================
def predict_future(df, df_key="global", periods=3):

    model = get_model(df_key, df)

    return {
        "forecast": model.predict(df, periods),
        "metrics": model.metrics,
        "model_cached": True
    }