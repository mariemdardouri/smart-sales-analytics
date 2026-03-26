# chat_service.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from services.basket_service import (
    df_all, 
    get_basket_analysis, 
    get_cooccurrence_analysis,
    get_categories,
    get_delegations
)
import re
import time
from typing import Dict, List, Optional

# Initialize the model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    api_key="AIzaSyCoBr6f8PBgPgyEKm9rL2q3_VAknzEnUtI",
    temperature=0.3,  # Réduire la température pour des réponses plus précises
    request_timeout=30,
    max_retries=2
)
print("✅ Modèle Gemini initialisé.")

# Variable pour stocker le contexte de la dernière conversation
last_context = {
    "region": None,
    "categorie": None,
    "top_n": 5
}

def extract_filters(question: str) -> dict:
    """
    Extrait les filtres potentiels de la question:
    - catégorie (boissons, électronique, etc.)
    - délégation/ville (Bizerte, Tunis, Sfax, etc.)
    - top_n (nombre de résultats)
    - single_product (si on veut un seul produit)
    """
    filters = {
        "categorie": None,
        "delegation": None,
        "top_n": 5,
        "single_product": False,
        "produits": [],
        "is_comparison": False,
        "comparison_regions": []
    }
    
    question_lower = question.lower()
    
    # Détecter si c'est une question de comparaison
    if any(keyword in question_lower for keyword in [
        "compar", "différence", "et a", "c est les memes", "même chose",
        "entre", "vs", "versus"
    ]):
        filters["is_comparison"] = True
    
    # Détecter si on veut un seul produit
    if any(keyword in question_lower for keyword in [
        "le produit le plus acheté", "le plus vendu", "le meilleur produit",
        "quel est le produit", "quel produit", "top 1", "un seul"
    ]):
        filters["single_product"] = True
        filters["top_n"] = 1
    
    # Extraire le nombre de résultats
    top_match = re.search(r'top (\d+)', question_lower)
    if top_match:
        filters["top_n"] = int(top_match.group(1))
        if filters["top_n"] == 1:
            filters["single_product"] = True
    
    # Extraire la catégorie - Passer df_all en argument
    categories = get_categories(df_all)
    for cat in categories:
        if cat.lower() in question_lower:
            filters["categorie"] = cat
            break
    
    # Extraire la délégation/ville - Passer df_all en argument
    delegations = get_delegations(df_all)
    mentioned_delegations = []
    for delg in delegations:
        if delg.lower() in question_lower:
            mentioned_delegations.append(delg)
            filters["delegation"] = delg
    
    # Pour les comparaisons, stocker toutes les régions mentionnées
    if len(mentioned_delegations) > 0:
        filters["comparison_regions"] = mentioned_delegations
    
    # Extraire les produits mentionnés
    product_pattern = r'"([^"]+)"|' + r"'([^']+)'"
    products = re.findall(product_pattern, question)
    if products:
        filters["produits"] = [p[0] or p[1] for p in products if p[0] or p[1]]
    
    return filters

def answer_top_products(question: str, filters: dict) -> str:
    """Répond aux questions sur les top produits"""
    global last_context
    
    try:
        df_filtered = df_all
        
        # Appliquer les filtres
        if filters["categorie"]:
            df_filtered = df_filtered[df_filtered["categorie"] == filters["categorie"]]
        
        if filters["delegation"]:
            df_filtered = df_filtered[df_filtered["délégation"] == filters["delegation"]]
        
        if df_filtered.empty:
            location = filters["delegation"] or "toute la Tunisie"
            category = filters["categorie"] or "toutes catégories"
            return f"Aucun produit trouvé pour {category} à {location}."
        
        # Top produits par fréquence d'achat
        top_products = (
            df_filtered["nom_produit"]
            .value_counts()
            .head(filters["top_n"])
        )
        
        if top_products.empty:
            return "Aucun produit trouvé."
        
        # Sauvegarder le contexte pour les questions suivantes
        if filters["delegation"]:
            last_context["region"] = filters["delegation"]
        if filters["categorie"]:
            last_context["categorie"] = filters["categorie"]
        last_context["top_n"] = filters["top_n"]
        
        # Formater la réponse selon si on veut un seul produit ou plusieurs
        if filters["single_product"]:
            product_name = top_products.index[0]
            count = top_products.values[0]
            
            response = "🏆 "
            if filters["categorie"]:
                response += f"**Le produit le plus acheté dans la catégorie '{filters['categorie']}'"
            elif filters["delegation"]:
                response += f"**Le produit le plus acheté à {filters['delegation']}"
            else:
                response += f"**Le produit le plus acheté**"
            
            response += f" est **{product_name}** avec **{count}** achats."
            return response
        
        else:
            response = f"🎯 **Top {len(top_products)} produits"
            if filters["categorie"]:
                response += f" dans la catégorie '{filters['categorie']}'"
            if filters["delegation"]:
                response += f" à {filters['delegation']}"
            response += ":**\n\n"
            
            for i, (product, count) in enumerate(top_products.items(), 1):
                response += f"{i}. **{product}** - {count} achats\n"
            
            return response
        
    except Exception as e:
        return f"Erreur lors de l'analyse des produits: {e}"

def answer_basket_analysis(question: str, filters: dict) -> str:
    """Répond aux questions sur les produits achetés ensemble"""
    try:
        # Si la question mentionne deux produits spécifiques
        if filters["produits"] and len(filters["produits"]) >= 2:
            result = get_cooccurrence_analysis(df_all, produits=filters["produits"][:2])
            if "error" not in result:
                confidence = result.get("confidence", 0)
                sont_souvent = result.get("sont_souvent_ensemble", False)
                recommandation = result.get("recommandation", "")
                
                response = f"🔍 **Analyse de co-occurrence**\n\n"
                response += f"Produits: **{result['produit1']}** et **{result['produit2']}**\n"
                response += f"✓ Achetés ensemble **{result['frequence_ensemble']}** fois\n"
                response += f"✓ Confiance: **{confidence:.1f}%**\n"
                
                if sont_souvent:
                    response += f"\n✨ **{recommandation}**\n"
                else:
                    response += "\n⚠️ Ces produits sont rarement achetés ensemble.\n"
                
                return response
            else:
                return f"Erreur: {result.get('error', 'Produits non trouvés')}"
        
        # Sinon, chercher les meilleures paires avec filtres
        else:
            pairs = get_basket_analysis(
                df_all,
                categorie=filters["categorie"],
                delegation=filters["delegation"],
                top_n=filters["top_n"]
            )
            
            if not pairs:
                location = filters["delegation"] or "toute la Tunisie"
                category = filters["categorie"] or "toutes catégories"
                return f"Aucune paire de produits trouvée pour {category} à {location}."
            
            response = f"🛒 **Top {len(pairs)} paires de produits achetés ensemble"
            if filters["categorie"]:
                response += f" dans la catégorie '{filters['categorie']}'"
            if filters["delegation"]:
                response += f" à {filters['delegation']}"
            response += ":**\n\n"
            
            for i, pair in enumerate(pairs, 1):
                produits = " et ".join(pair["produits"])
                frequence = pair["frequence"]
                response += f"{i}. **{produits}** - {frequence} fois\n"
            
            return response
            
    except Exception as e:
        return f"Erreur lors de l'analyse des paires: {e}"

def answer_comparison_question(question: str, filters: dict) -> Optional[str]:
    """Compare les ventes entre différentes régions ou catégories"""
    global last_context
    
    question_lower = question.lower()
    
    # Récupérer les régions mentionnées - Passer df_all en argument
    delegations = get_delegations(df_all)
    mentioned_regions = []
    
    for delg in delegations:
        if delg.lower() in question_lower:
            mentioned_regions.append(delg)
    
    # Si c'est une question "et a ariana c'est les memes ?"
    if "c est les memes" in question_lower or "même chose" in question_lower or "et a" in question_lower:
        if len(mentioned_regions) == 1 and last_context["region"]:
            # Comparer avec la région précédente
            region1 = last_context["region"]
            region2 = mentioned_regions[0]
            
            df_region1 = df_all[df_all["délégation"] == region1]
            df_region2 = df_all[df_all["délégation"] == region2]
            
            # Récupérer le top 3 produits pour chaque région
            top_region1 = df_region1["nom_produit"].value_counts().head(3)
            top_region2 = df_region2["nom_produit"].value_counts().head(3)
            
            response = f"📊 **Comparaison entre {region1} et {region2}**\n\n"
            response += f"**{region1}** (top 3 produits):\n"
            for i, (product, count) in enumerate(top_region1.items(), 1):
                response += f"  {i}. {product} - {count} achats\n"
            
            response += f"\n**{region2}** (top 3 produits):\n"
            for i, (product, count) in enumerate(top_region2.items(), 1):
                response += f"  {i}. {product} - {count} achats\n"
            
            # Analyser si les produits sont similaires
            common_products = set(top_region1.index) & set(top_region2.index)
            if common_products:
                response += f"\n✨ **Produits communs**: {', '.join(common_products)}\n"
            else:
                response += f"\n⚠️ Les produits les plus vendus sont différents dans ces deux régions.\n"
            
            return response
    
    # Si la question mentionne explicitement deux régions
    elif len(mentioned_regions) >= 2:
        region1, region2 = mentioned_regions[0], mentioned_regions[1]
        
        df_region1 = df_all[df_all["délégation"] == region1]
        df_region2 = df_all[df_all["délégation"] == region2]
        
        # Récupérer le top 5 produits pour chaque région
        top_region1 = df_region1["nom_produit"].value_counts().head(5)
        top_region2 = df_region2["nom_produit"].value_counts().head(5)
        
        response = f"📊 **Comparaison détaillée entre {region1} et {region2}**\n\n"
        response += f"**{region1}** (top 5):\n"
        for i, (product, count) in enumerate(top_region1.items(), 1):
            response += f"  {i}. {product} - {count} achats\n"
        
        response += f"\n**{region2}** (top 5):\n"
        for i, (product, count) in enumerate(top_region2.items(), 1):
            response += f"  {i}. {product} - {count} achats\n"
        
        return response
    
    return None

def answer_general_question(question: str) -> str:
    """Utilise Gemini pour répondre aux questions générales avec fallback"""
    system_prompt = (
        "Tu es un assistant spécialisé en analyse de ventes pour une entreprise tunisienne. "
        "Tu as accès aux données de ventes contenant des informations sur:\n"
        "- Produits: noms, catégories, marques\n"
        "- Ventes: dates, quantités, prix\n"
        "- Clients: délégations, localités\n\n"
        "Réponds aux questions de manière claire, concise et professionnelle. "
        "Utilise des chiffres et des données quand c'est pertinent. "
        "Si la question concerne des analyses spécifiques (top produits, paires, etc.), "
        "oriente vers ces analyses. Si tu ne sais pas, dis 'Je ne sais pas'."
    )
    
    try:
        # Ajouter un petit délai pour éviter les rate limits
        time.sleep(0.5)
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ])
        return response.content
    except Exception as e:
        error_msg = str(e)
        # Fallback quand l'API est limitée
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "⚠️ **Limite d'utilisation atteinte**\n\n" \
                   "Je suis actuellement très sollicité(e). Voici ce que je peux faire sans utiliser l'IA:\n" \
                   "• Donner le top produits par région ou catégorie\n" \
                   "• Analyser les produits achetés ensemble\n" \
                   "• Comparer les ventes entre régions\n\n" \
                   "Posez-moi une question comme:\n" \
                   "- 'Quel est le produit le plus acheté à Bizerte?'\n" \
                   "- 'Quels sont les produits achetés ensemble?'\n" \
                   "- 'Compare les ventes entre Tunis et Sfax'"
        return f"❌ **Erreur technique**: {error_msg[:200]}"

def ask_chatbot(question: str) -> str:
    """
    Répond aux questions envoyées par le frontend.
    Analyse intelligemment la question et utilise les fonctions appropriées.
    """
    question_lower = question.lower()
    
    # Extraire les filtres de la question
    filters = extract_filters(question)
    
    # Vérifier si c'est une question de comparaison
    if filters["is_comparison"] or "et a" in question_lower:
        comparison_result = answer_comparison_question(question, filters)
        if comparison_result:
            return comparison_result
    
    # Déterminer le type de question
    is_top_products = any(keyword in question_lower for keyword in [
        "top produit", "plus acheté", "meilleur vente", "produit phare",
        "best seller", "le plus vendu", "quel est le produit", 
        "quel produit", "produit le plus"
    ])
    
    is_basket_analysis = any(keyword in question_lower for keyword in [
        "achetés ensemble", "co-occurrence", "souvent ensemble",
        "ensemble", "avec", "pair", "paire", "panier"
    ])
    
    is_categories = any(keyword in question_lower for keyword in [
        "catégorie", "type de produit", "famille", "categories"
    ])
    
    # Répondre selon le type de question
    if is_top_products:
        return answer_top_products(question, filters)
    
    elif is_basket_analysis:
        return answer_basket_analysis(question, filters)
    
    elif is_categories:
        categories = get_categories(df_all)
        response = "📦 **Catégories de produits disponibles:**\n\n"
        for i, cat in enumerate(categories, 1):
            response += f"{i}. {cat}\n"
        return response
    
    else:
        # Pour les questions générales, vérifier d'abord les comparaisons
        comparison_result = answer_comparison_question(question, filters)
        if comparison_result:
            return comparison_result
        
        # Si c'est une question sur les régions ou catégories mais pas explicite
        categories = get_categories(df_all)
        if any(cat.lower() in question_lower for cat in categories):
            return answer_top_products(question, filters)
        
        delegations = get_delegations(df_all)
        if any(delg.lower() in question_lower for delg in delegations):
            return answer_top_products(question, filters)
        
        # Utiliser l'API Gemini pour les questions générales
        return answer_general_question(question)