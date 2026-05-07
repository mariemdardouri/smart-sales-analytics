import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

class SalesPredictorV2:
    def __init__(self, model_path="models/sales_model_v2.pkl"):
        self.model = None
        self.preprocessor = None
        self.model_path = model_path
        self.is_trained = False
        self.metrics = {}
        self.feature_importance = {}
        self.available_localites = []
    
    def train(self, df, test_size=0.2):
        """Entraîne le modèle"""
        print("Entraînement du modèle...")
        
        # Préparer les données
        data = df.copy()
        data['date_dachat'] = pd.to_datetime(data['date_dachat'])
        data['month'] = data['date_dachat'].dt.month
        
        # Nettoyer les prix
        data['prix_total'] = pd.to_numeric(data['prix_total'], errors='coerce')
        data = data.dropna(subset=['prix_total', 'categorie', 'délégation', 'localité'])
        
        print(f"  Données après nettoyage: {len(data)} lignes")
        
        # Agrégation par catégorie, délégation, localité ET mois
        features = data.groupby(['categorie', 'délégation', 'localité', 'month']).agg({
            'prix_total': 'sum'
        }).reset_index()
        
        features.columns = ['categorie', 'delegation', 'localite', 'month', 'chiffre_affaires']
        
        self.available_localites = features['localite'].unique().tolist()
        
        print(f"  Données après agrégation: {len(features)} lignes")
        print(f"  Catégories: {features['categorie'].nunique()}")
        print(f"  Délégations: {features['delegation'].nunique()}")
        print(f"  Localités: {features['localite'].nunique()}")
        
        # Features
        X = features[['categorie', 'delegation', 'localite', 'month']]
        y = features['chiffre_affaires']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        print(f"\n  Train size: {len(X_train)}")
        print(f"  Test size: {len(X_test)}")
        
        # Préprocesseur
        categorical_features = ['categorie', 'delegation', 'localite']
        numerical_features = ['month']
        
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ])
        
        # Modèle
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Pipeline
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('regressor', self.model)
        ])
        
        # Entraînement
        print("  Entraînement en cours...")
        pipeline.fit(X_train, y_train)
        
        # Évaluation
        y_pred_train = pipeline.predict(X_train)
        y_pred_test = pipeline.predict(X_test)
        
        self.metrics = {
            'train': {
                'r2': r2_score(y_train, y_pred_train),
                'mae': mean_absolute_error(y_train, y_pred_train),
                'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train))
            },
            'test': {
                'r2': r2_score(y_test, y_pred_test),
                'mae': mean_absolute_error(y_test, y_pred_test),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
            }
        }
        
        # Feature importance
        cat_features = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
        all_features = numerical_features + list(cat_features)
        importances = self.model.feature_importances_
        self.feature_importance = dict(zip(all_features, importances))
        
        self.is_trained = True
        self.print_metrics()
        self.save_model()
        
        print("✅ Modèle entraîné avec succès!")
        return self
    
    def print_metrics(self):
        """Affiche les métriques"""
        print("\n" + "="*50)
        print("MÉTRIQUES DU MODÈLE")
        print("="*50)
        print(f"Train R²: {self.metrics['train']['r2']:.4f}")
        print(f"Test R²:  {self.metrics['test']['r2']:.4f}")
        print(f"Train MAE: {self.metrics['train']['mae']:.2f} DT")
        print(f"Test MAE:  {self.metrics['test']['mae']:.2f} DT")
        print("="*50)
        
        if self.feature_importance:
            print("\nTop 15 features importantes:")
            sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:15]
            for i, (feature, importance) in enumerate(sorted_features):
                print(f"  {i+1}. {feature}: {importance:.4f}")
    
    def predict_sales(self, categories, delegation=None, localite=None, month=None):
        """
        Prédit le chiffre d'affaires
        - month = None: retourne la SOMME des 12 mois (annuel)
        - month = 1-12: retourne la valeur pour CE mois uniquement
        """
        if not self.is_trained:
            return {"error": "Modèle non entraîné"}
        
        results = []
        
        for categorie in categories:
            delegation_val = delegation if delegation else 'Tunis'
            localite_val = localite if localite else 'Tunis'
            
            if month is not None:
                pred_data = pd.DataFrame({
                    'categorie': [categorie],
                    'delegation': [delegation_val],
                    'localite': [localite_val],
                    'month': [month]
                })
                
                try:
                    X_pred = self.preprocessor.transform(pred_data)
                    prediction = self.model.predict(X_pred)[0]
                    
                    results.append({
                        'categorie': categorie,
                        'delegation': delegation_val,
                        'localite': localite_val,
                        'month': month,
                        'chiffre_affaires_predit': round(float(prediction), 2),
                        'period_type': 'month'
                    })
                except Exception as e:
                    print(f"Erreur: {e}")
                    results.append({
                        'categorie': categorie,
                        'delegation': delegation_val,
                        'localite': localite_val,
                        'month': month,
                        'chiffre_affaires_predit': 0,
                        'period_type': 'month'
                    })
            else:
                total_annuel = 0
                details_mois = []
                
                for m in range(1, 13):
                    pred_data = pd.DataFrame({
                        'categorie': [categorie],
                        'delegation': [delegation_val],
                        'localite': [localite_val],
                        'month': [m]
                    })
                    
                    try:
                        X_pred = self.preprocessor.transform(pred_data)
                        prediction = self.model.predict(X_pred)[0]
                        total_annuel += prediction
                        details_mois.append({
                            'month': m,
                            'chiffre_affaires': round(float(prediction), 2)
                        })
                    except Exception as e:
                        print(f"Erreur mois {m}: {e}")
                        details_mois.append({
                            'month': m,
                            'chiffre_affaires': 0
                        })
                
                results.append({
                    'categorie': categorie,
                    'delegation': delegation_val,
                    'localite': localite_val,
                    'chiffre_affaires_predit': round(float(total_annuel), 2),
                    'details_par_mois': details_mois,
                    'period_type': 'year'
                })
        
        total_ca = sum([r['chiffre_affaires_predit'] for r in results])
        
        if month is not None:
            note = f"Prédiction mensuelle pour {localite_val} - Mois {month}"
        else:
            note = f"Prédiction ANNUELLE pour {localite_val} (somme des 12 mois)"
        
        return {
            'success': True,
            'predictions': results,
            'total_chiffre_affaires': round(total_ca, 2),
            'nombre_categories': len(categories),
            'note': note,
            'period_type': 'month' if month else 'year'
        }
    
    def get_available_categories(self, df):
        return sorted(df['categorie'].dropna().unique().tolist())
    
    def get_available_delegations(self, df):
        return sorted(df['délégation'].dropna().unique().tolist())
    
    def get_available_localites(self, df, delegation=None):
        if delegation:
            localites = df[df['délégation'] == delegation]['localité'].dropna().unique()
        else:
            localites = df['localité'].dropna().unique()
        return sorted(localites.tolist())
    
    def save_model(self):
        try:
            pipeline = Pipeline([
                ('preprocessor', self.preprocessor),
                ('regressor', self.model)
            ])
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'pipeline': pipeline,
                    'metrics': self.metrics,
                    'feature_importance': self.feature_importance,
                    'available_localites': self.available_localites
                }, f)
            print(f"✅ Modèle sauvegardé: {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def load_model(self):
        if not os.path.exists(self.model_path):
            return False
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            pipeline = data['pipeline']
            self.preprocessor = pipeline.named_steps['preprocessor']
            self.model = pipeline.named_steps['regressor']
            self.metrics = data['metrics']
            self.feature_importance = data['feature_importance']
            self.available_localites = data.get('available_localites', [])
            self.is_trained = True
            print(f"✅ Modèle chargé: {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False

__all__ = ['SalesPredictorV2']