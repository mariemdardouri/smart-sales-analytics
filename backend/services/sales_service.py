from utils.preprocessing import load_data
from models.sales_modele_v2 import SalesPredictorV2
import pandas as pd


print("Chargement des données...")
df_all = load_data()

df_all['date_dachat'] = pd.to_datetime(df_all['date_dachat'], errors='coerce')
df_all['prix_total'] = pd.to_numeric(df_all['prix_total'], errors='coerce')

print(f"Données chargées: {len(df_all)} lignes")


sales_predictor = SalesPredictorV2(model_path="models/sales_model_v2.pkl")

print("Tentative de chargement du modèle de ventes...")
if not sales_predictor.load_model():
    print("Aucun modèle trouvé — entraînement en cours...")
    sales_predictor.train(df_all)
    print("Modèle entraîné et sauvegardé !")
else:
    print("Modèle chargé — prêt à l'emploi !")

def get_available_categories():
    return sales_predictor.get_available_categories(df_all)

def get_available_delegations():
    return sales_predictor.get_available_delegations(df_all)

def get_available_localites(delegation=None):
    return sales_predictor.get_available_localites(df_all, delegation)

def predict_sales(categories, delegation=None, localite=None, month=None):
    return sales_predictor.predict_sales(categories, delegation, localite, month)

def get_model_metrics():
    if sales_predictor.is_trained:
        return sales_predictor.metrics
    return {"error": "Modèle non entraîné"}

def get_feature_importance():
    if sales_predictor.is_trained:
        return sales_predictor.feature_importance
    return {"error": "Modèle non entraîné"}