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

    # ------------------------------------------------------------------
    # ENTRAÎNEMENT
    # ------------------------------------------------------------------
    def train(self, df):
        print("Début de l'entraînement du modèle de co-occurrences...")

        self.df_all = df.copy()
        df = df.copy()
        df["nom_produit"] = df["nom_produit"].fillna("").astype(str).str.strip()
        df = df[df["nom_produit"] != ""]

        # ── Clé de transaction ─────────────────────────────────────────
        # On s'assure que la colonne transaction existe déjà
        # (construite dans basket_service.py), sinon on la crée ici
        if "transaction" not in df.columns:
            df["date_dachat"] = pd.to_datetime(df["date_dachat"], errors="coerce")
            df["transaction"] = (
                df["client_id"].astype(str)
                + "_"
                + df["date_dachat"].dt.strftime("%Y-%m-%d")
            )

        self.product_names = sorted(df["nom_produit"].unique().tolist())
        print(f"Produits uniques : {len(self.product_names)}")

        # ── Diagnostic : taille des transactions ──────────────────────
        trans_sizes = df.groupby("transaction")["nom_produit"].count()
        print(f"\n📊 Diagnostic transactions :")
        print(f"   Nombre total de transactions : {len(trans_sizes)}")
        print(f"   Taille moyenne d'un panier   : {trans_sizes.mean():.1f} produits")
        print(f"   Taille max                   : {trans_sizes.max()} produits")
        print(f"   Transactions avec 1 seul produit : {(trans_sizes == 1).sum()} "
              f"({(trans_sizes == 1).mean()*100:.0f}%)")
        print(f"   Transactions avec ≥2 produits    : {(trans_sizes >= 2).sum()} "
              f"({(trans_sizes >= 2).mean()*100:.0f}%)")

        if trans_sizes.mean() < 1.5:
            print("\n⚠️  ATTENTION : La majorité des transactions ne contient qu'un seul")
            print("   produit → la clé client_id+date est probablement trop granulaire.")
            print("   Essayez de regrouper par client_id seul ou par semaine.")

        # ── Calcul des co-occurrences ──────────────────────────────────
        transactions = df.groupby("transaction")["nom_produit"].apply(list)

        pair_counts = Counter()
        self.product_support = Counter()

        print("\nCalcul des co-occurrences...")
        for idx, items in enumerate(transactions):
            if idx % 10000 == 0 and idx > 0:
                print(f"  {idx}/{len(transactions)}...")

            unique_items = list({str(i).strip() for i in items if str(i).strip()})

            for item in unique_items:
                self.product_support[item] += 1

            if len(unique_items) >= 2:
                for combo in combinations(sorted(unique_items), 2):
                    pair_counts[combo] += 1

        self.pair_frequencies = dict(pair_counts)
        self.total_transactions = len(transactions)

        print(f"\nPaires uniques   : {len(self.pair_frequencies)}")
        print(f"Transactions     : {self.total_transactions}")

        # ── Top 10 paires pour vérification ───────────────────────────
        print("\n🔝 Top 10 paires les plus fréquentes :")
        top10 = Counter(self.pair_frequencies).most_common(10)
        for (p1, p2), freq in top10:
            sup1 = self.product_support[p1]
            sup2 = self.product_support[p2]
            conf = round(freq / sup1 * 100, 1)
            expected = (sup1 * sup2) / self.total_transactions
            lift = round(freq / expected, 2) if expected > 0 else 0
            print(f"   {p1} + {p2} → freq={freq}, conf={conf}%, lift={lift}")

        self.save_model()
        return self

    # ------------------------------------------------------------------
    # RECHERCHE D'UN PRODUIT
    # ------------------------------------------------------------------
    def find_product_match(self, product_name):
        if not product_name or not self.product_names:
            return None

        name_lower = product_name.lower().strip()

        # 1. Correspondance exacte
        for p in self.product_names:
            if p.lower() == name_lower:
                return p

        # 2. Le produit commence par la recherche
        for p in self.product_names:
            if p.lower().startswith(name_lower):
                return p

        # 3. Tous les mots de la recherche présents dans le produit
        words = re.findall(r'\b\w+\b', name_lower)
        if words:
            best = None
            best_score = 0
            for p in self.product_names:
                p_words = re.findall(r'\b\w+\b', p.lower())
                matched = sum(1 for w in words if w in p_words)
                if matched > best_score:
                    best_score = matched
                    best = p
            if best_score > 0:
                return best

        # 4. Sous-chaîne
        if len(name_lower) >= 4:
            for p in self.product_names:
                if name_lower in p.lower():
                    return p

        return None

    # ------------------------------------------------------------------
    # ANALYSE D'UNE PAIRE
    # ------------------------------------------------------------------
    def analyze_pair(self, product1: str, product2: str,
                     categorie: str = None, delegation: str = None) -> dict:

        matched1 = self.find_product_match(product1)
        matched2 = self.find_product_match(product2)

        if not matched1 or not matched2:
            missing = []
            if not matched1:
                missing.append(product1)
            if not matched2:
                missing.append(product2)
            return {
                "produit1": product1,
                "produit2": product2,
                "error": f"Produit(s) non trouvé(s) : {', '.join(missing)}",
                "confidence": 0,
                "frequence_ensemble": 0,
                "frequence_produit1": 0,
                "frequence_produit2": 0,
                "sont_souvent_ensemble": False,
                "recommandation": f"Produit(s) non trouvé(s) : {', '.join(missing)}",
                "details": {"conseil": "Vérifiez les noms des produits."},
            }

        # ── Filtrage optionnel ─────────────────────────────────────────
        df_f = self.df_all.copy()

        if categorie and "categorie" in df_f.columns:
            df_f = df_f[df_f["categorie"] == categorie]

        if delegation and "délégation" in df_f.columns:
            df_f = df_f[df_f["délégation"] == delegation]

        # S'assurer que la colonne transaction existe
        if "transaction" not in df_f.columns:
            df_f["date_dachat"] = pd.to_datetime(df_f["date_dachat"], errors="coerce")
            df_f["transaction"] = (
                df_f["client_id"].astype(str)
                + "_"
                + df_f["date_dachat"].dt.strftime("%Y-%m-%d")
            )

        # ── Calcul des fréquences sur le sous-ensemble filtré ──────────
        trans_prod1 = set(df_f[df_f["nom_produit"] == matched1]["transaction"])
        trans_prod2 = set(df_f[df_f["nom_produit"] == matched2]["transaction"])

        freq1 = len(trans_prod1)
        freq2 = len(trans_prod2)
        freq_together = len(trans_prod1 & trans_prod2)
        total = df_f["transaction"].nunique()

        confidence = round((freq_together / freq1) * 100, 1) if freq1 > 0 else 0.0
        confidence_rev = round((freq_together / freq2) * 100, 1) if freq2 > 0 else 0.0

        # Lift : mesure si les deux produits sont achetés PLUS souvent
        # ensemble qu'attendu par hasard (lift > 1 = association réelle)
        expected = (freq1 * freq2) / total if total > 0 else 0
        lift = round(freq_together / expected, 2) if expected > 0 else 0.0

        # ── Score composite ────────────────────────────────────────────
        # On prend la confiance MAX (produit le moins fréquent en dénominateur)
        # et on la multiplie par le lift pour ne garder que les vraies associations
        conf_max = max(confidence, confidence_rev)

        # Score = confiance_max (%) × lift × log(1 + freq_ensemble)
        # Un lift < 1 → association négative → score proche de 0
        # Un lift ≥ 1 + conf_max élevée → bon score
        if lift >= 1:
            score = round(conf_max * lift * np.log1p(freq_together), 2)
        else:
            # Pénaliser les associations négatives (lift < 1)
            score = round(conf_max * lift, 2)

        print(f"\n🔍 Analyse : {matched1} + {matched2}")
        print(f"   freq1={freq1}, freq2={freq2}, ensemble={freq_together}")
        print(f"   conf(1→2)={confidence}%, conf(2→1)={confidence_rev}%")
        print(f"   lift={lift}, score={score}")

        # ── Recommandation basée sur le score ──────────────────────────
        if score >= 50:
            ensemble = True
            recommandation = (
                f'🔥 "{matched1}" et "{matched2}" sont fortement associés.'
            )
            conseil = "Séparez ces produits en rayon pour maximiser les ventes croisées."

        elif score >= 20:
            ensemble = True
            recommandation = (
                f'⚠️ "{matched1}" et "{matched2}" sont souvent achetés ensemble.'
            )
            conseil = "Placez-les dans des rayons proches mais pas côte à côte."

        elif score >= 5:
            ensemble = False
            recommandation = (
                f'ℹ️ "{matched1}" et "{matched2}" ont une association modérée.'
            )
            conseil = "Placement libre, pas de contrainte particulière."

        elif lift >= 1 and freq_together > 0:
            ensemble = False
            recommandation = (
                f'ℹ️ "{matched1}" et "{matched2}" sont achetés ensemble {freq_together} fois — association faible mais réelle.'
            )
            conseil = "Placement libre."

        else:
            ensemble = False
            recommandation = (
                f'✅ "{matched1}" et "{matched2}" ne sont pas significativement associés.'
            )
            conseil = "Aucune contrainte de placement."

        return {
            "produit1": matched1,
            "produit2": matched2,
            "frequence_produit1": freq1,
            "frequence_produit2": freq2,
            "frequence_ensemble": freq_together,
            "confidence": confidence,
            "confidence_inverse": confidence_rev,
            "lift": lift,
            "score": score,
            "sont_souvent_ensemble": ensemble,
            "recommandation": recommandation,
            "details": {"conseil": conseil},
        }

    # ------------------------------------------------------------------
    # RECOMMANDATIONS PAR CO-OCCURRENCE
    # ------------------------------------------------------------------
    def get_cooccurrence_recommendations(self, product, top_n=5, min_confidence=5):
        matched = self.find_product_match(product)
        if not matched or matched not in self.product_support:
            return []

        related_counts = Counter()
        for (p1, p2), count in self.pair_frequencies.items():
            if p1 == matched:
                related_counts[p2] += count
            elif p2 == matched:
                related_counts[p1] += count

        product_count = self.product_support[matched]
        results = []

        for related_prod, freq in related_counts.items():
            conf = (freq / product_count) * 100
            related_count = self.product_support[related_prod]
            expected = (product_count * related_count) / self.total_transactions if self.total_transactions else 0
            lift = round(freq / expected, 2) if expected > 0 else 0

            results.append({
                "produit": related_prod,
                "confiance": round(conf, 1),
                "frequence_ensemble": freq,
                "frequence_produit": product_count,
                "lift": lift,
            })

        results.sort(key=lambda x: x["lift"], reverse=True)  # Trier par lift
        filtered = [r for r in results if r["confiance"] >= min_confidence]
        return filtered[:top_n] if filtered else results[:top_n]

    # ------------------------------------------------------------------
    # PERSISTANCE
    # ------------------------------------------------------------------
    def save_model(self):
        try:
            model_data = {
                "product_names": self.product_names,
                "pair_frequencies": self.pair_frequencies,
                "product_support": self.product_support,
                "total_transactions": self.total_transactions,
                "df_all": self.df_all,
            }
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(model_data, f)
            print("Modèle sauvegardé ✓")
            return True
        except Exception as e:
            print(f"Erreur sauvegarde : {e}")
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

            print(f"Modèle chargé ✓  ({len(self.product_names)} produits, "
                  f"{len(self.pair_frequencies)} paires, "
                  f"{self.total_transactions} transactions)")
            return True
        except Exception as e:
            print(f"Erreur chargement : {e}")
            return False


__all__ = ['BasketRecommender']