from sklearn.cluster import KMeans
from utils.preprocessing import preprocess_customer

df = preprocess_customer()

X = df[["prix_total", "quantité_achetée", "Panier_Moyen"]]

model = KMeans(n_clusters=3, random_state=42)
df["cluster"] = model.fit_predict(X)

def get_clusters():
    return df[["client_id", "cluster"]].to_dict(orient="records")