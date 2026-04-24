from utils.preprocessing import get_clean_df
from models.location_model_v3 import LocationModel
import pandas as pd


print("Chargement des données pour Location Model…")

try:
    df = get_clean_df()
    df["prix_total"] = pd.to_numeric(df["prix_total"], errors="coerce")
    print(f"Données chargées : {len(df):,} lignes")
except Exception as e:
    print(f"❌ Erreur chargement données : {e}")
    df = pd.DataFrame()

model = LocationModel(model_path="models/location_model.pkl")

print("Tentative de chargement du modèle location…")
if not model.load_model():
    if not df.empty:
        print("Entraînement du modèle location…")
        model.train(df)
    else:
        print("⚠️  Pas de données — modèle non disponible.")
else:
    print("Modèle location prêt !")




def get_available_categories() -> list:
    return model.get_available_categories()


def get_all_regions() -> list:
    return model.get_all_regions()


def get_best_region(
    category: str     = None,
    brand: str        = None,
    product_name: str = None,
    top_n: int        = 5,
) -> dict:
    if not model.is_trained:
        return {"success": False, "error": "Modèle non disponible."}
    return model.predict(
        category=category,
        brand=brand,
        product_name=product_name,
        top_n=top_n,
    )


def get_model_metrics() -> dict:
    return model.get_metrics()