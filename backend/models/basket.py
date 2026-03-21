import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from itertools import combinations
import pickle
import os

class BasketRecommender:
    def __init__(self, model_path="models/basket_model.pkl"):
        self.product_names = []
        self.product_features = None
        self.vectorizer = None
        self.pair_frequencies = {}
        self.product_support = Counter()  # Fréquence d'apparition de chaque produit
        self.total_transactions = 0
        self.model_path = model_path
        
    def train(self, df):
        """
        Entraîne le modèle sur les données historiques
        """
        print("Début de l'entraînement du modèle...")
        
        # Nettoyer les données
        df = df.dropna(subset=['nom_produit'])
        
        # 1. Récupérer tous les produits uniques
        self.product_names = df['nom_produit'].unique().tolist()
        print(f"Nombre de produits uniques: {len(self.product_names)}")
        
        # 2. Créer des caractéristiques pour la similarité sémantique
        feature_columns = [df['nom_produit'].fillna('')]
        if 'categorie' in df.columns:
            feature_columns.append(df['categorie'].fillna(''))
        if 'marque' in df.columns:
            feature_columns.append(df['marque'].fillna(''))
        
        df['product_features'] = feature_columns[0]
        for col in feature_columns[1:]:
            df['product_features'] = df['product_features'] + " " + col
        
        # 3. Vectoriser les caractéristiques des produits
        unique_products = df.drop_duplicates('nom_produit')
        unique_features = unique_products['product_features'].tolist()
        
        if len(unique_features) > 1:
            self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
            self.product_features = self.vectorizer.fit_transform(unique_features)
        
        # 4. Analyser les co-occurrences dans les transactions
        transactions = df.groupby("transaction")["nom_produit"].apply(list)
        
        # Compter toutes les paires
        pair_counts = Counter()
        self.total_transactions = 0
        
        for items in transactions:
            unique_items = [str(i) for i in set(items) if pd.notna(i)]
            
            # Compter la fréquence de chaque produit
            for item in unique_items:
                self.product_support[item] += 1
            
            if len(unique_items) >= 2:
                combos = list(combinations(sorted(unique_items), 2))
                pair_counts.update(combos)
                self.total_transactions += 1
        
        # Stocker les fréquences des paires avec support
        self.pair_frequencies = {}
        for (p1, p2), count in pair_counts.items():
            key = tuple(sorted([p1, p2]))
            self.pair_frequencies[key] = count
        
        print(f"Nombre de paires uniques: {len(self.pair_frequencies)}")
        print(f"Nombre de transactions analysées: {self.total_transactions}")
        print(f"Nombre de produits avec support: {len(self.product_support)}")
        
        # Sauvegarder le modèle
        self.save_model()
        
        return self
    
    def get_cooccurrence_recommendations(self, product, top_n=5, min_confidence=5):
        """
        Trouve les produits qui apparaissent le plus souvent avec le produit donné
        Retourne uniquement les recommandations avec une confiance > min_confidence
        """
        recommendations = []
        
        # Vérifier si le produit existe
        if product not in self.product_support:
            return []
        
        # Compter les fréquences des produits qui apparaissent avec celui-ci
        related_counts = Counter()
        for (p1, p2), count in self.pair_frequencies.items():
            if p1 == product:
                related_counts[p2] += count
            elif p2 == product:
                related_counts[p1] += count
        
        # Support du produit (nombre de transactions contenant ce produit)
        product_count = self.product_support[product]
        
        # Calculer la confiance pour chaque produit associé
        recommendations_list = []
        for related_prod, freq in related_counts.items():
            # Confiance = P(produit_associé | produit) = fréquence_ensemble / fréquence_produit
            confidence = (freq / product_count) * 100
            
            # Calculer aussi le lift (optionnel)
            related_count = self.product_support[related_prod]
            expected_freq = (product_count * related_count) / self.total_transactions if self.total_transactions > 0 else 0
            lift = freq / expected_freq if expected_freq > 0 else 0
            
            recommendations_list.append({
                'produit': related_prod,
                'confiance': round(confidence, 1),
                'frequence_ensemble': freq,
                'frequence_produit': product_count,
                'lift': round(lift, 2)
            })
        
        # Trier par confiance décroissante
        recommendations_list.sort(key=lambda x: x['confiance'], reverse=True)
        
        # Filtrer pour ne garder que les recommandations avec une confiance minimale
        filtered_recs = [r for r in recommendations_list if r['confiance'] >= min_confidence]
        
        if filtered_recs:
            return filtered_recs[:top_n]
        else:
            # Si aucune recommandation avec confiance suffisante, retourner un message clair
            return []
    
    def predict_recommendations(self, product_names, top_n=5, min_confidence=5):
        """
        Prédit les recommandations pour une liste de produits
        """
        recommendations = {}
        
        for product in product_names:
            product = product.strip()
            product_lower = product.lower()
            
            # 1. Vérifier si le produit existe directement
            direct_matches = [p for p in self.product_names if p.lower() == product_lower]
            
            if direct_matches:
                matched_product = direct_matches[0]
                recs = self.get_cooccurrence_recommendations(matched_product, top_n, min_confidence)
                
                if recs:
                    recommendations[product] = {
                        'type': 'direct',
                        'matched_product': matched_product,
                        'recommendations': recs,
                        'has_recommendations': True
                    }
                else:
                    # Le produit existe mais n'est jamais acheté avec d'autres produits
                    recommendations[product] = {
                        'type': 'direct',
                        'matched_product': matched_product,
                        'recommendations': [],
                        'has_recommendations': False,
                        'message': f'Le produit "{matched_product}" existe mais n\'a jamais été acheté avec d\'autres produits dans l\'historique des ventes.'
                    }
            
            # 2. Si pas de correspondance directe, chercher des produits similaires
            else:
                similar = self.find_similar_products(product, top_n=5)
                
                if similar:
                    # Chercher les recommandations des produits similaires
                    aggregated_recs = {}
                    for sim in similar:
                        sim_recs = self.get_cooccurrence_recommendations(sim['produit'], top_n=3, min_confidence=min_confidence)
                        for rec in sim_recs:
                            if rec['produit'] not in aggregated_recs:
                                weight = sim['similarite'] / 100
                                aggregated_recs[rec['produit']] = {
                                    'produit': rec['produit'],
                                    'confiance': round(rec['confiance'] * weight, 1),
                                    'sources': [sim['produit']]
                                }
                    
                    final_recs = sorted(aggregated_recs.values(), key=lambda x: x['confiance'], reverse=True)[:top_n]
                    
                    if final_recs:
                        recommendations[product] = {
                            'type': 'similar',
                            'similar_products': similar,
                            'recommendations': final_recs,
                            'has_recommendations': True
                        }
                    else:
                        recommendations[product] = {
                            'type': 'similar',
                            'similar_products': similar,
                            'recommendations': [],
                            'has_recommendations': False,
                            'message': 'Des produits similaires ont été trouvés, mais aucun n\'a de recommandations disponibles.'
                        }
                else:
                    recommendations[product] = {
                        'type': 'not_found',
                        'message': f'Produit "{product}" non trouvé dans la base de données',
                        'recommendations': [],
                        'has_recommendations': False
                    }
        
        return recommendations
    
    def find_similar_products(self, product_name, top_n=5, threshold=0.3):
        """
        Trouve les produits similaires par nom
        """
        if not self.vectorizer or self.product_features is None:
            return []
        
        try:
            product_vector = self.vectorizer.transform([product_name])
            similarities = cosine_similarity(product_vector, self.product_features)[0]
            top_indices = similarities.argsort()[-top_n:][::-1]
            
            similar_products = []
            unique_products = []
            
            for idx in top_indices:
                if similarities[idx] >= threshold and idx < len(self.product_names):
                    product = self.product_names[idx]
                    if product.lower() != product_name.lower() and product not in unique_products:
                        unique_products.append(product)
                        similar_products.append({
                            'produit': product,
                            'similarite': round(similarities[idx] * 100, 1)
                        })
            
            return similar_products
        except Exception as e:
            print(f"Erreur lors de la recherche de produits similaires: {e}")
            return []
    
    def save_model(self):
        """Sauvegarde le modèle entraîné"""
        try:
            model_data = {
                'product_names': self.product_names,
                'product_features': self.product_features,
                'pair_frequencies': self.pair_frequencies,
                'product_support': self.product_support,
                'total_transactions': self.total_transactions,
                'vectorizer': self.vectorizer,
            }
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"Modèle sauvegardé avec succès dans {self.model_path}")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_model(self):
        """Charge un modèle pré-entraîné"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.product_names = model_data['product_names']
                self.product_features = model_data['product_features']
                self.pair_frequencies = model_data['pair_frequencies']
                self.product_support = model_data.get('product_support', Counter())
                self.total_transactions = model_data.get('total_transactions', 0)
                self.vectorizer = model_data['vectorizer']
                
                print(f"Modèle chargé avec succès depuis {self.model_path}")
                print(f"Produits chargés: {len(self.product_names)}")
                print(f"Paires chargées: {len(self.pair_frequencies)}")
                print(f"Transactions: {self.total_transactions}")
                return True
            except Exception as e:
                print(f"Erreur lors du chargement: {e}")
                return False
        return False