from mlxtend.frequent_patterns import apriori, association_rules
from utils.preprocessing import load_data

def get_product_bundles():
    df = load_data()

    basket = df.groupby(
        ["date_dachat", "nom_produit"]
    )["quantité_achetée"].sum().unstack().fillna(0)

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)

    frequent = apriori(basket, min_support=0.02, use_colnames=True)

    rules = association_rules(frequent, metric="lift", min_threshold=1)

    bundles = []

    for _, row in rules.iterrows():
        bundles.append({
            "produits_ensemble": list(row["antecedents"]),
            "produits_recommandes": list(row["consequents"]),
            "confidence": float(row["confidence"])
        })

    return bundles[:10]