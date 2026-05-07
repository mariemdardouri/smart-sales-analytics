import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import LabelEncoder
import pickle
import os
import warnings
warnings.filterwarnings('ignore')


class LocationModel:
  

    def __init__(self, model_path="models/location_model.pkl"):
        self.model_path   = model_path
        self.is_trained   = False
        self.model        = None
        self.le_cat       = LabelEncoder()
        self.le_reg       = LabelEncoder()

        self.available_regions    = []
        self.available_categories = []
        self.metrics              = {}

      
        self.cat_region_stats   = {}   
        self.region_global_mean = {}   
        self.cat_global_mean    = {}   
        self.global_mean        = 0.0

       
        self._df_raw = None

    def train(self, df: pd.DataFrame):
        print("\n" + "=" * 60)
        print("  ENTRAÎNEMENT — LOCATION MODEL (Random Forest)")
        print("=" * 60)

   
        cols = [c for c in ["categorie", "délégation", "prix_total",
                             "marque", "nom_produit"] if c in df.columns]
        self._df_raw = df[cols].copy()
        self._df_raw["prix_total"] = pd.to_numeric(
            self._df_raw["prix_total"], errors="coerce")
        self._df_raw = self._df_raw.dropna(
            subset=["prix_total", "categorie", "délégation"])

        print(f"  Lignes valides       : {len(self._df_raw):,}")

     
        agg = (
            self._df_raw
            .groupby(["categorie", "délégation"])["prix_total"]
            .sum()
            .reset_index()
            .rename(columns={"délégation": "region", "prix_total": "ca_total"})
        )
        print(f"  Combinaisons cat×reg : {len(agg):,}")

        self.available_regions    = sorted(agg["region"].unique().tolist())
        self.available_categories = sorted(agg["categorie"].unique().tolist())
        self.global_mean          = float(agg["ca_total"].mean())

    
        for cat, grp in agg.groupby("categorie"):
            self.cat_region_stats[cat] = dict(zip(grp["region"], grp["ca_total"]))

        self.region_global_mean = (
            agg.groupby("region")["ca_total"].mean().to_dict())
        self.cat_global_mean = (
            agg.groupby("categorie")["ca_total"].mean().to_dict())

     
        agg["cat_enc"]      = self.le_cat.fit_transform(agg["categorie"])
        agg["reg_enc"]      = self.le_reg.fit_transform(agg["region"])
        agg["reg_ca_mean"]  = agg["reg_enc"].map(
            agg.groupby("reg_enc")["ca_total"].mean())
        agg["cat_ca_mean"]  = agg["cat_enc"].map(
            agg.groupby("cat_enc")["ca_total"].mean())

        X = agg[["cat_enc", "reg_enc", "reg_ca_mean", "cat_ca_mean"]].values
        y = agg["ca_total"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        print(f"  Train : {len(X_train)} | Test : {len(X_test)}")

     
        self.model = RandomForestRegressor(
            n_estimators=60,
            max_depth=7,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        )
        print("  Entraînement en cours…")
        self.model.fit(X_train, y_train)

      
        r2_train  = r2_score(y_train, self.model.predict(X_train))
        r2_test   = r2_score(y_test,  self.model.predict(X_test))
        mae       = mean_absolute_error(y_test, self.model.predict(X_test))
        mape      = mean_absolute_percentage_error(
                        y_test, self.model.predict(X_test)) * 100
        gap       = r2_train - r2_test

        if gap > 0.15:
            overfit = f"⚠️  Overfitting détecté  (gap = {gap:.3f} > 0.15)"
        elif gap > 0.05:
            overfit = f"🟡 Légère différence train/test  (gap = {gap:.3f})"
        else:
            overfit = f"🟢 Pas d'overfitting  (gap = {gap:.3f})"

        if r2_test >= 0.85 and mape <= 20:
            interp = "🟢 Excellent — modèle très fiable."
        elif r2_test >= 0.70 and mape <= 35:
            interp = "🟡 Bon — prédictions fiables dans l'ensemble."
        elif r2_test >= 0.50:
            interp = "🟠 Acceptable — tendances correctes, valeurs approx."
        else:
            interp = "🔴 Faible — utilisez comme indicateur seulement."

        self.metrics = {
            "r2_train":        round(r2_train, 4),
            "r2_test":         round(r2_test,  4),
            "overfit_gap":     round(gap,       4),
            "overfit_status":  overfit,
            "mae":             round(mae,        2),
            "mape":            round(mape,       1),
            "train_size":      int(len(X_train)),
            "test_size":       int(len(X_test)),
            "regions_count":   len(self.available_regions),
            "categories_count":len(self.available_categories),
            "interpretation":  interp,
        }

        self._print_metrics()
        self.is_trained = True
        self.save_model()
        return self

    def _print_metrics(self):
        m = self.metrics
        print("\n" + "=" * 60)
        print("  MÉTRIQUES DU MODÈLE")
        print("=" * 60)
        print(f"  R² TRAIN : {m['r2_train']}   ← fit sur données d'entraînement")
        print(f"  R² TEST  : {m['r2_test']}   ← généralisation sur données inconnues")
        print(f"  {m['overfit_status']}")
        print(f"  MAE      : {m['mae']:>12,.0f} DT  (erreur absolue moyenne)")
        print(f"  MAPE     : {m['mape']:>11.1f} %   (erreur % moyenne)")
        print(f"  Train    : {m['train_size']} échantillons")
        print(f"  Test     : {m['test_size']} échantillons")
        print(f"  {m['interpretation']}")
        print("=" * 60 + "\n")

   
    def predict(
        self,
        category: str    = None,
        brand: str       = None,
        product_name: str= None,
        top_n: int       = 5,
    ) -> dict:

        if not self.is_trained:
            return {"success": False, "error": "Modèle non entraîné."}

       
        resolved_cat  = self._resolve_category(category)
        is_known_cat  = resolved_cat in self.cat_region_stats


        filtered_stats = None
        note           = None

        if (brand and brand.strip()) or (product_name and product_name.strip()):
            filtered_stats, note = self._filter_stats(
                resolved_cat, brand, product_name)

  
        results = []
        for region in self.available_regions:
            if filtered_stats is not None:
                ca = filtered_stats.get(region, 0)
                if ca == 0:
                 
                    ca = self._predict_ca(resolved_cat, region, is_known_cat) * 0.1
            else:
                ca = self._predict_ca(resolved_cat, region, is_known_cat)

            results.append({"region": region, "ca_predit": ca})

      
        results.sort(key=lambda x: x["ca_predit"], reverse=True)
        top    = results[:top_n]
        max_ca = top[0]["ca_predit"] if top and top[0]["ca_predit"] > 0 else 1

        for r in top:
            r["score"]      = round((r["ca_predit"] / max_ca) * 100, 1)
            r["ca_predit"]  = round(r["ca_predit"], 2)
            r["confidence"] = (
                "Élevée"  if r["score"] >= 75 else
                "Moyenne" if r["score"] >= 45 else
                "Faible"
            )

        response = {
            "success":      True,
            "best_region":  top[0]["region"]   if top else None,
            "best_ca":      top[0]["ca_predit"] if top else 0,
            "best_score":   top[0]["score"]     if top else 0,
            "top_regions":  top,
            "input": {
                "categorie":       resolved_cat,
                "marque":          brand,
                "produit":         product_name,
                "categorie_connue":is_known_cat,
                "filtre_applique": filtered_stats is not None,
            },
            "model_metrics": self.metrics,
        }
        if note:
            response["note"] = note

        return response

  
    def _resolve_category(self, category: str) -> str:
        if not category:
            return self.available_categories[0] if self.available_categories else ""
        if category in self.cat_region_stats:
            return category
        lower_map = {c.lower(): c for c in self.available_categories}
        if category.lower() in lower_map:
            return lower_map[category.lower()]
        for c in self.available_categories:
            if category.lower() in c.lower() or c.lower() in category.lower():
                return c
        return category  

    def _filter_stats(self, category, brand, product_name):
        """Filtre le DataFrame brut et retourne {region: ca} ou (None, note)."""
        if self._df_raw is None:
            return None, "Données brutes non disponibles."

        df = self._df_raw[self._df_raw["categorie"] == category].copy()

        if brand and brand.strip() and "marque" in df.columns:
            mask = df["marque"].str.contains(brand.strip(), case=False, na=False)
            if mask.any():
                df = df[mask]
            else:
                return None, (
                    f"Marque \"{brand}\" absente de l'historique — "
                    f"prédiction basée sur la catégorie \"{category}\"."
                )

        if product_name and product_name.strip() and "nom_produit" in df.columns:
            mask = df["nom_produit"].str.contains(
                product_name.strip(), case=False, na=False)
            if mask.any():
                df = df[mask]
            else:
                return None, (
                    f"Produit \"{product_name}\" absent de l'historique — "
                    f"prédiction basée sur la catégorie \"{category}\"."
                )

        if df.empty:
            return None, "Aucune donnée après filtrage."

        stats = df.groupby("délégation")["prix_total"].sum().to_dict()
        return stats, None

    def _predict_ca(self, category: str, region: str, is_known_cat: bool) -> float:
  
        if is_known_cat and region in self.cat_region_stats.get(category, {}):
            lv = self.cat_region_stats[category][region]
            try:
                cat_enc = self.le_cat.transform([category])[0]
                reg_enc = self.le_reg.transform([region])[0]
                X = np.array([[
                    cat_enc, reg_enc,
                    self.region_global_mean.get(region, lv),
                    self.cat_global_mean.get(category, lv),
                ]])
                ml = self.model.predict(X)[0]
                return 0.6 * lv + 0.4 * ml
            except Exception:
                return lv

    
        if is_known_cat:
            return self.cat_global_mean.get(category, 0) * self._reg_factor(region)

    
        return self.global_mean * self._reg_factor(region)

    def _reg_factor(self, region: str) -> float:
        if not self.region_global_mean:
            return 1.0
        g = np.mean(list(self.region_global_mean.values()))
        return self.region_global_mean.get(region, g) / g if g else 1.0

    def get_available_categories(self): return self.available_categories
    def get_all_regions(self):          return self.available_regions
    def get_metrics(self):              return self.metrics

   
    def save_model(self):
        try:
           
            base = os.path.dirname(os.path.abspath(__file__))
            path = os.path.abspath(os.path.join(base, "../models/location_model.pkl"))
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "wb") as f:
                pickle.dump({
                    "model":               self.model,
                    "le_cat":              self.le_cat,
                    "le_reg":              self.le_reg,
                    "available_regions":   self.available_regions,
                    "available_categories":self.available_categories,
                    "cat_region_stats":    self.cat_region_stats,
                    "region_global_mean":  self.region_global_mean,
                    "cat_global_mean":     self.cat_global_mean,
                    "global_mean":         self.global_mean,
                    "metrics":             self.metrics,
                    "_df_raw":             self._df_raw,
                }, f)
            print(f"✅ Modèle sauvegardé → {path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde : {e}")
            return False

    def load_model(self):
    
        base = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.abspath(
            os.path.join(base, "../models/location_model.pkl"))
        path = abs_path if os.path.exists(abs_path) else self.model_path

        if not os.path.exists(path):
            return False
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)

            self.model                = data["model"]
            self.le_cat               = data["le_cat"]
            self.le_reg               = data["le_reg"]
            self.available_regions    = data["available_regions"]
            self.available_categories = data["available_categories"]
            self.cat_region_stats     = data["cat_region_stats"]
            self.region_global_mean   = data["region_global_mean"]
            self.cat_global_mean      = data["cat_global_mean"]
            self.global_mean          = data["global_mean"]
            self.metrics              = data["metrics"]
            self._df_raw              = data.get("_df_raw")
            self.is_trained           = True

            print(f"✅ Modèle chargé ← {path}")
            print(f"   {len(self.available_categories)} catégories | "
                  f"{len(self.available_regions)} régions")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement : {e}")
            return False


__all__ = ["LocationModel"]