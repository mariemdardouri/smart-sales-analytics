import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
import pickle
import os
import re
import warnings
warnings.filterwarnings('ignore')

class BasketRecommender:
    def __init__(self, model_path="models/basket_model.pkl"):
        self.product_names = []
        self.pair_frequencies = {}
        self.product_support = Counter()
        self.total_transactions = 0
        self.model_path = model_path
        self.df_all = None

    def train(self, df):
        """Entraîne le modèle basé sur les co-occurrences"""
        print("Début de l'entraînement du modèle de co-occurrences...")
        
        self.df_all = df.copy()
        df = df.copy()
        df["nom_produit"] = df["nom_produit"].fillna("").astype(str).str.strip()
        df = df[df["nom_produit"] != ""]
        
        df["transaction"] = (
            df["client_id"].astype(str) + "_" + 
            df["date_dachat"].dt.strftime("%Y-%m-%d")
        )
        
        self.product_names = sorted(df["nom_produit"].unique().tolist())
        print(f"Produits uniques : {len(self.product_names)}")
        
        print("\nExemples de produits dans la base:")
        produits_hygiene = [p for p in self.product_names if "shampooing" in p.lower() or "déodorant" in p.lower()][:10]
        for p in produits_hygiene:
            print(f"  - {p}")
        
        transactions = df.groupby("transaction")["nom_produit"].apply(list)
        
        pair_counts = Counter()
        self.product_support = Counter()
        
        print("Calcul des co-occurrences...")
        for idx, items in enumerate(transactions):
            if idx % 10000 == 0 and idx > 0:
                print(f"  Traitement transaction {idx}/{len(transactions)}...")
            
            unique_items = []
            for item in items:
                item_clean = str(item).strip()
                if item_clean:
                    unique_items.append(item_clean)
            unique_items = list(set(unique_items))
            
            if not unique_items:
                continue
            
            for item in unique_items:
                self.product_support[item] += 1
            
            if len(unique_items) >= 2:
                for combo in combinations(sorted(unique_items), 2):
                    pair_counts[combo] += 1
        
        self.pair_frequencies = dict(pair_counts)
        self.total_transactions = len(transactions)
        
        print(f"Paires uniques: {len(self.pair_frequencies)}")
        print(f"Transactions: {self.total_transactions}")
        
        self.save_model()
        return self

    def find_product_match(self, product_name):
        if not product_name or not self.product_names:
            return None
        
        product_name_lower = product_name.lower().strip()
        
        for product in self.product_names:
            if product.lower() == product_name_lower:
                return product
        
        for product in self.product_names:
            if product.lower().startswith(product_name_lower):
                return product
        
        words = re.findall(r'\b\w+\b', product_name_lower)
        for product in self.product_names:
            product_words = re.findall(r'\b\w+\b', product.lower())
            if any(word in product_words for word in words):
                return product
        
        if len(product_name_lower) >= 4:
            for product in self.product_names:
                if product_name_lower in product.lower():
                    if len(product) < len(product_name_lower) * 3:
                        return product
        
        return None

    def analyze_pair(self, product1: str, product2: str, categorie: str = None, delegation: str = None) -> dict:
        if self.df_all is None:
            return {"error": "Modèle non entraîné"}

        matched1 = self.find_product_match(product1)
        matched2 = self.find_product_match(product2)

        if not matched1 or not matched2:
            return {"error": "Produit non trouvé"}

        df_f = self.df_all.copy()

        if categorie and "categorie" in df_f.columns:
            df_f = df_f[df_f["categorie"] == categorie]

        if delegation and "délégation" in df_f.columns:
            df_f = df_f[df_f["délégation"] == delegation]

        df_f["transaction"] = (
            df_f["client_id"].astype(str) + "_" + 
            df_f["date_dachat"].dt.strftime("%Y-%m-%d")
        )

        trans_prod1 = set(df_f[df_f["nom_produit"] == matched1]["transaction"])
        trans_prod2 = set(df_f[df_f["nom_produit"] == matched2]["transaction"])

        freq1 = len(trans_prod1)
        freq2 = len(trans_prod2)
        freq_together = len(trans_prod1 & trans_prod2)

        confidence = round((freq_together / freq1) * 100, 1) if freq1 > 0 else 0

        total_transactions = len(df_f["transaction"].unique())
        expected = (freq1 * freq2) / total_transactions if total_transactions > 0 else 0
        lift = round(freq_together / expected, 2) if expected > 0 else 0

        # 🔥 SCORE INTELLIGENT
        score = round(confidence * lift * np.log1p(freq_together), 2)

        # 🔥 LOGIQUE BASÉE SUR LE SCORE
        if score >= 50:
            recommandation = f'🔥 "{matched1}" et "{matched2}" sont fortement associés (score: {score})'
            conseil = "Séparez ces produits pour maximiser les ventes"
            ensemble = True

        elif score >= 20:
            recommandation = f'⚠️ "{matched1}" et "{matched2}" sont souvent achetés ensemble (score: {score})'
            conseil = "Placez-les dans des rayons proches"
            ensemble = True

        elif score >= 5:
            recommandation = f'ℹ️ "{matched1}" et "{matched2}" ont une association faible (score: {score})'
            conseil = "Placement libre"
            ensemble = False

        else:
            recommandation = f'✅ "{matched1}" et "{matched2}" ne sont pas significativement associés (score: {score})'
            conseil = "Aucune contrainte"
            ensemble = False

        return {
            "produit1": matched1,
            "produit2": matched2,
            "frequence_produit1": freq1,
            "frequence_produit2": freq2,
            "frequence_ensemble": freq_together,
            "confidence": confidence,
            "lift": lift,
            "score": score,
            "sont_souvent_ensemble": ensemble,
            "recommandation": recommandation,
            "details": {"conseil": conseil}
        }

    def save_model(self):
        try:
            model_data = {
                "product_names": self.product_names,
                "pair_frequencies": self.pair_frequencies,
                "product_support": self.product_support,
                "total_transactions": self.total_transactions,
                "df_all": self.df_all
            }
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(model_data, f)
            print("Modèle sauvegardé")
            return True
        except Exception as e:
            print(e)
            return False

    def load_model(self):
        if not os.path.exists(self.model_path):
            return False
        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.product_names = model_data["product_names"]
            self.pair_frequencies = model_data["pair_frequencies"]
            self.product_support = model_data["product_support"]
            self.total_transactions = model_data["total_transactions"]
            self.df_all = model_data.get("df_all")

            print("Modèle chargé")
            return True
        except Exception as e:
            print(e)
            return False


__all__ = ['BasketRecommender']