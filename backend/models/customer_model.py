from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from utils.preprocessing import preprocess_customer

df = preprocess_customer()

X = df[["prix_total", "quantité_achetée", "Panier_Moyen"]]
y = df["HighValue"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

def predict_customer(total, qty):

    panier = total / qty if qty != 0 else 0

    pred = model.predict([[total, qty, panier]])

    return int(pred[0])