import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_CACHE = {}

def create_features(df):
    df = df.copy()
    df["ds"] = pd.to_datetime(df["ds"])

    df["month"] = df["ds"].dt.month
    df["year"] = df["ds"].dt.year
    df["quarter"] = df["ds"].dt.quarter

    df["lag1"] = df["y"].shift(1)
    df["lag2"] = df["y"].shift(2)
    df["lag3"] = df["y"].shift(3)

    return df.dropna()

class XGBoostForecastModel:

    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8
        )

        self.feature_cols = ["month", "year", "quarter", "lag1", "lag2", "lag3"]
        self.metrics = {}

    def train(self, df):

        df = create_features(df)

        if len(df) < 10:
            self.metrics = {"error": "Not enough data"}
            return self

        split = int(len(df) * 0.8)

        train = df.iloc[:split]
        test = df.iloc[split:]

        if len(test) == 0:
            self.metrics = {"error": "No test data"}
            return self

        X_train = train[self.feature_cols]
        y_train = train["y"]

        X_test = test[self.feature_cols]
        y_test = test["y"]

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)

        self.metrics = {
            "MAE": float(mean_absolute_error(y_test, preds)),
            "RMSE": float(np.sqrt(mean_squared_error(y_test, preds))),
            "R2": float(r2_score(y_test, preds)) if len(y_test) > 1 else None
        }

        return self

    def predict(self, df, periods=3):

        df = df.copy()
        df["ds"] = pd.to_datetime(df["ds"])

        history = df.copy()
        predictions = []

        for _ in range(periods):

            last_date = history["ds"].max()
            next_date = last_date + pd.DateOffset(months=1)

            row = {
                "ds": next_date,
                "month": next_date.month,
                "year": next_date.year,
                "quarter": next_date.quarter,
                "lag1": history["y"].iloc[-1],
                "lag2": history["y"].iloc[-2] if len(history) > 1 else 0,
                "lag3": history["y"].iloc[-3] if len(history) > 2 else 0,
            }

            X_pred = pd.DataFrame([row])[self.feature_cols]
            yhat = float(self.model.predict(X_pred)[0])

            yhat = max(0, yhat)

            predictions.append({
                "ds": next_date.strftime("%Y-%m"),
                "yhat": yhat
            })

            history = pd.concat([
                history,
                pd.DataFrame([{"ds": next_date, "y": yhat}])
            ], ignore_index=True)

        return predictions


def predict_future_xgb(df, df_key="global", periods=3):

    if df_key not in MODEL_CACHE:
        MODEL_CACHE[df_key] = XGBoostForecastModel().train(df)

    model = MODEL_CACHE[df_key]

    return {
        "forecast": model.predict(df, periods),
        "metrics": model.metrics,
        "model": "xgboost"
    }