from utils.preprocessing import load_data

def geo_analysis():
    df = load_data()

    geo = df.groupby(["délégation", "nom_produit"])["quantité_achetée"] \
            .sum().reset_index()

    result = {}

    for city in geo["délégation"].unique():
        top = geo[geo["délégation"] == city] \
              .sort_values(by="quantité_achetée", ascending=False) \
              .head(5)

        result[city] = top["nom_produit"].tolist()

    return result