import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import os
import warnings
import json
from datetime import datetime
warnings.filterwarnings('ignore')

class SalesPredictor:
    def __init__(self, model_path="models/sales_model.pkl"):
        self.model = None
        self.preprocessor = None
        self.model_path = model_path
        self.is_trained = False
        self.metrics = {}
        self.feature_importance = {}
        self.model_type = "RandomForest"
        
    def prepare_features(self, df):
        """
        Prépare les features pour l'entraînement
        """
        # Créer une copie
        data = df.copy()
        
        # Features temporelles
        data['date_dachat'] = pd.to_datetime(data['date_dachat'])
        data['month'] = data['date_dachat'].dt.month
        data['day_of_week'] = data['date_dachat'].dt.dayofweek
        data['day_of_month'] = data['date_dachat'].dt.day
        data['week_of_year'] = data['date_dachat'].dt.isocalendar().week
        
        # Features produit
        data['prix_unitaire'] = pd.to_numeric(data['prix_unitaire'], errors='coerce')
        data['quantité_achetée'] = pd.to_numeric(data['quantité_achetée'], errors='coerce')
        
        # Calculer le chiffre d'affaires si non présent
        if 'prix_total' not in data.columns:
            data['prix_total'] = data['prix_unitaire'] * data['quantité_achetée']
        
        # Aggréger par catégorie, délégation, mois
        features = data.groupby(['categorie', 'délégation', 'localité', 'month', 'day_of_week']).agg({
            'prix_total': 'sum',
            'quantité_achetée': 'sum',
            'prix_unitaire': 'mean'
        }).reset_index()
        
        features.columns = ['categorie', 'delegation', 'localite', 'month', 'day_of_week', 
                           'chiffre_affaires', 'quantite_totale', 'prix_moyen']
        
        return features
    
    def train(self, df, model_type="RandomForest", test_size=0.2):
        """
        Entraîne le modèle de prédiction des ventes
        """
        print("="*60)
        print("ENTRAÎNEMENT DU MODÈLE DE PRÉDICTION DES VENTES")
        print("="*60)
        
        # Préparer les features
        print("\n📊 Préparation des données...")
        features_df = self.prepare_features(df)
        
        # Définir les features et la target
        feature_cols = ['categorie', 'delegation', 'localite', 'month', 'day_of_week']
        X = features_df[feature_cols]
        y = features_df['chiffre_affaires']
        
        print(f"  Dataset size: {len(X)} échantillons")
        print(f"  Features: {feature_cols}")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        print(f"\n  Train size: {len(X_train)}")
        print(f"  Test size: {len(X_test)}")
        
        # Créer le préprocesseur
        categorical_features = ['categorie', 'delegation', 'localite']
        numerical_features = ['month', 'day_of_week']
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
            ])
        
        # Choisir le modèle
        if model_type == "RandomForest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "GradientBoosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif model_type == "Ridge":
            self.model = Ridge(alpha=1.0, random_state=42)
        else:
            self.model = RandomForestRegressor(random_state=42)
        
        # Créer le pipeline
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('regressor', self.model)
        ])
        
        print(f"\n🔄 Entraînement du modèle {model_type}...")
        pipeline.fit(X_train, y_train)
        
        # Prédictions
        y_pred_train = pipeline.predict(X_train)
        y_pred_test = pipeline.predict(X_test)
        
        # Calcul des métriques
        self.metrics = {
            'train': {
                'r2': r2_score(y_train, y_pred_train),
                'mae': mean_absolute_error(y_train, y_pred_train),
                'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'mape': np.mean(np.abs((y_train - y_pred_train) / y_train)) * 100
            },
            'test': {
                'r2': r2_score(y_test, y_pred_test),
                'mae': mean_absolute_error(y_test, y_pred_test),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'mape': np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
            }
        }
        
        # Cross-validation
        print("\n📊 Cross-validation...")
        cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='r2')
        self.metrics['cv_mean'] = cv_scores.mean()
        self.metrics['cv_std'] = cv_scores.std()
        
        # Feature importance (pour RandomForest)
        if model_type in ["RandomForest", "GradientBoosting"]:
            # Récupérer les feature names après one-hot encoding
            cat_features = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
            all_features = numerical_features + list(cat_features)
            
            importances = self.model.feature_importances_
            self.feature_importance = dict(zip(all_features, importances))
            self.feature_importance = dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        self.model_type = model_type
        self.is_trained = True
        
        # Afficher les résultats
        self.print_metrics()
        
        # Sauvegarder le modèle
        self.save_model()
        
        print("\n✅ Modèle entraîné avec succès!")
        return self
    
    def print_metrics(self):
        """
        Affiche les métriques du modèle
        """
        print("\n" + "="*60)
        print("📈 MÉTRIQUES DU MODÈLE")
        print("="*60)
        
        print(f"\nModèle: {self.model_type}")
        print(f"\n--- ENTRAÎNEMENT ---")
        print(f"  R² Score:     {self.metrics['train']['r2']:.4f}")
        print(f"  MAE:          {self.metrics['train']['mae']:.2f} DT")
        print(f"  RMSE:         {self.metrics['train']['rmse']:.2f} DT")
        print(f"  MAPE:         {self.metrics['train']['mape']:.2f}%")
        
        print(f"\n--- TEST ---")
        print(f"  R² Score:     {self.metrics['test']['r2']:.4f}")
        print(f"  MAE:          {self.metrics['test']['mae']:.2f} DT")
        print(f"  RMSE:         {self.metrics['test']['rmse']:.2f} DT")
        print(f"  MAPE:         {self.metrics['test']['mape']:.2f}%")
        
        print(f"\n--- CROSS-VALIDATION (5 folds) ---")
        print(f"  R² moyen:     {self.metrics['cv_mean']:.4f} (+/- {self.metrics['cv_std']*2:.4f})")
        
        if self.feature_importance:
            print(f"\n--- IMPORTANCE DES FEATURES ---")
            for i, (feature, importance) in enumerate(list(self.feature_importance.items())[:10]):
                print(f"  {i+1}. {feature}: {importance:.4f}")
    
    def predict_sales(self, categories, delegation=None, localite=None, month=None):
        """
        Prédit le chiffre d'affaires pour une ou plusieurs catégories
        """
        if not self.is_trained:
            return {"error": "Modèle non entraîné"}
        
        # Créer le dataframe de prédiction
        predictions = []
        
        # Si month n'est pas spécifié, utiliser tous les mois
        months = [month] if month else list(range(1, 13))
        
        for categorie in categories:
            for month_val in months:
                for day in [1, 8, 15, 22]:  # Échantillon de jours
                    pred_data = pd.DataFrame({
                        'categorie': [categorie],
                        'delegation': [delegation if delegation else 'Toutes'],
                        'localite': [localite if localite else 'Toutes'],
                        'month': [month_val],
                        'day_of_week': [day % 7]
                    })
                    
                    # Prédire
                    try:
                        # Recharger le pipeline
                        with open(self.model_path, 'rb') as f:
                            pipeline = pickle.load(f)
                        
                        prediction = pipeline.predict(pred_data)[0]
                        
                        predictions.append({
                            'categorie': categorie,
                            'delegation': delegation,
                            'localite': localite,
                            'month': month_val,
                            'chiffre_affaires_predit': round(float(prediction), 2)
                        })
                    except:
                        predictions.append({
                            'categorie': categorie,
                            'delegation': delegation,
                            'localite': localite,
                            'month': month_val,
                            'chiffre_affaires_predit': 0,
                            'error': "Erreur de prédiction"
                        })
        
        # Aggréger par catégorie
        result = {}
        for pred in predictions:
            cat = pred['categorie']
            if cat not in result:
                result[cat] = {
                    'categorie': cat,
                    'chiffre_affaires_total': 0,
                    'details': []
                }
            result[cat]['chiffre_affaires_total'] += pred['chiffre_affaires_predit']
            result[cat]['details'].append(pred)
        
        # Calculer le total général
        total_ca = sum([r['chiffre_affaires_total'] for r in result.values()])
        
        return {
            'success': True,
            'predictions': list(result.values()),
            'total_chiffre_affaires': round(total_ca, 2),
            'nombre_categories': len(categories),
            'model_metrics': self.metrics,
            'feature_importance': self.feature_importance
        }
    
    def get_available_categories(self, df):
        """
        Récupère la liste des catégories disponibles
        """
        return sorted(df['categorie'].dropna().unique().tolist())
    
    def get_available_delegations(self, df):
        """
        Récupère la liste des délégations disponibles
        """
        return sorted(df['délégation'].dropna().unique().tolist())
    
    def get_available_localites(self, df, delegation=None):
        """
        Récupère la liste des localités disponibles
        """
        if delegation:
            localites = df[df['délégation'] == delegation]['localité'].dropna().unique()
        else:
            localites = df['localité'].dropna().unique()
        return sorted(localites.tolist())
    
    def save_model(self):
        """
        Sauvegarde le modèle et le préprocesseur
        """
        try:
            # Créer le pipeline complet
            pipeline = Pipeline([
                ('preprocessor', self.preprocessor),
                ('regressor', self.model)
            ])
            
            model_data = {
                'pipeline': pipeline,
                'model_type': self.model_type,
                'metrics': self.metrics,
                'feature_importance': self.feature_importance,
                'training_date': datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✅ Modèle sauvegardé → {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def load_model(self):
        """
        Charge le modèle
        """
        if not os.path.exists(self.model_path):
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            pipeline = model_data['pipeline']
            self.preprocessor = pipeline.named_steps['preprocessor']
            self.model = pipeline.named_steps['regressor']
            self.model_type = model_data['model_type']
            self.metrics = model_data['metrics']
            self.feature_importance = model_data['feature_importance']
            self.is_trained = True
            
            print(f"✅ Modèle chargé → {self.model_path}")
            print(f"  Type: {self.model_type}")
            print(f"  R² Score (test): {self.metrics['test']['r2']:.4f}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False


__all__ = ['SalesPredictor']