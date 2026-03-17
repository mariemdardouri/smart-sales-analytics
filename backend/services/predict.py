from models.customer_model import predict_customer
from models.forecast import get_forecast

def get_sales_forecast():
    return get_forecast()

def get_customer_prediction(total, qty):
    return predict_customer(total, qty)