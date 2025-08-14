"""
Application Streamlit pour la prédiction de churn client.

Cette application permet de prédire si un client bancaire est susceptible 
de quitter la banque (churn) en utilisant un modèle de machine learning.
"""
import streamlit as st
import logging
from typing import Dict, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports des modules locaux
from config.settings import Settings
from config.constants import Gender, Country, Category, BinaryChoice
from data.schemas import CustomerData
from data.validator import DataValidator
from models.predictor import ChurnPredictor
from ui.components import InputComponents, DisplayComponents
from utils.exceptions import ChurnPredictionError


def configure_page():
    """Configure la page Streamlit."""
    st.set_page_config(
        page_title=Settings.APP_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout=Settings.LAYOUT
    )


def render_sidebar():
    """Affiche la barre latérale avec les informations."""
    with st.sidebar:
        st.header("ℹ️ À propos")
        st.write(
            "Cette application utilise un modèle Random Forest "
            "pour prédire le risque de churn client."
        )
        
        st.header("📋 Instructions")
        st.write(
            "1. Remplissez tous les champs du formulaire\n"
            "2. Cliquez sur 'Prédire le churn'\n"
            "3. Consultez le résultat et les recommandations"
        )
        
        st.header("🎯 Interprétation")
        st.write("**Probabilité de churn :**")
        st.write("• 🟢 < 30% : Risque faible")
        st.write("• 🟡 30-70% : Risque moyen") 
        st.write("• 🔴 > 70% : Risque élevé")


def collect_user_inputs() -> Dict[str, Any]:
    """
    Collecte les données saisies par l'utilisateur.
    
    Returns:
        Dictionnaire contenant toutes les données saisies
    """
    st.header("📝 Saisie des Données Client")
    
    # Organisation en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Informations Personnelles")
        
        age = InputComponents.render_numeric_input(
            "Âge", "age", 
            "Âge du client en années"
        )
        
        gender = InputComponents.render_selectbox(
            "Sexe", Gender,
            "Sexe du client"
        )
        
        country = InputComponents.render_selectbox(
            "Pays", Country,
            "Pays de résidence du client"
        )
        
        category = InputComponents.render_selectbox(
            "Catégorie", Category,
            "Catégorie de compte du client"
        )
        
        st.subheader("🏦 Informations Bancaires")
        
        credit_score = InputComponents.render_numeric_input(
            "Score de Crédit", "credit_score",
            "Score de crédit du client (300-900)"
        )
        
        tenure = InputComponents.render_slider_input(
            "Ancienneté (années)", "tenure",
            "Nombre d'années depuis l'ouverture du compte"
        )
    
    with col2:
        st.subheader("💰 Informations Financières")
        
        balance = InputComponents.render_numeric_input(
            "Solde du Compte (€)", "balance",
            "Solde actuel du compte principal"
        )
        
        estimated_salary = InputComponents.render_numeric_input(
            "Salaire Estimé (€)", "estimated_salary",
            "Salaire annuel estimé du client"
        )
        
        num_of_products = InputComponents.render_slider_input(
            "Nombre de Produits", "num_of_products",
            "Nombre de produits bancaires utilisés"
        )
        
        point_earned = InputComponents.render_numeric_input(
            "Points Gagnés", "point_earned",
            "Points de fidélité accumulés"
        )
        
        st.subheader("🔍 Comportement Client")
        
        has_credit_card = InputComponents.render_selectbox(
            "Possède une Carte de Crédit", BinaryChoice,
            "Le client possède-t-il une carte de crédit ?"
        )
        
        is_active_member = InputComponents.render_selectbox(
            "Membre Actif", BinaryChoice,
            "Le client est-il un membre actif ?"
        )
        
        complain = InputComponents.render_selectbox(
            "A Déposé une Plainte", BinaryChoice,
            "Le client a-t-il déposé une plainte récemment ?"
        )
        
        satisfaction_score = InputComponents.render_slider_input(
            "Score de Satisfaction", "satisfaction_score",
            "Score de satisfaction client (0-5)"
        )
    
    return {
        'credit_score': int(credit_score),
        'age': int(age),
        'tenure': int(tenure),
        'balance': float(balance),
        'num_of_products': int(num_of_products),
        'estimated_salary': float(estimated_salary),
        'satisfaction_score': int(satisfaction_score),
        'point_earned': int(point_earned),
        'has_credit_card': has_credit_card,
        'is_active_member': is_active_member,
        'complain': complain,
        'gender': gender,
        'country': country,
        'category': category
    }


def main():
    """Fonction principale de l'application."""
    # Configuration de la page
    configure_page()
    
    # Titre principal
    st.title(Settings.APP_TITLE)
    
    # Barre latérale
    render_sidebar()
    
    try:
        # Initialisation du prédicteur
        predictor = ChurnPredictor()
        
        # Collecte des données utilisateur
        user_data = collect_user_inputs()
        
        # Bouton de prédiction
        if st.button("🎯 Prédire le Churn", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                
                # Validation des données
                validation_errors = DataValidator.validate_customer_data(user_data)
                business_errors = DataValidator.validate_business_rules(user_data)
                all_errors = validation_errors + business_errors
                
                if DisplayComponents.render_error_message(all_errors):
                    st.stop()
                
                # Création de l'objet CustomerData
                customer_data = CustomerData(**user_data)
                
                # Affichage du profil client
                DisplayComponents.render_customer_summary(customer_data)
                
                # Prédiction
                result = predictor.predict(customer_data)
                
                # Affichage du résultat
                DisplayComponents.render_prediction_result(result, customer_data)
                
                # Log de la prédiction
                logger.info(
                    f"Prédiction effectuée - Client: {customer_data.age}ans, "
                    f"{customer_data.country.value}, Résultat: {result.prediction}, "
                    f"Probabilité: {result.probability:.3f}"
                )
    
    except ChurnPredictionError as e:
        st.error(f"❌ Erreur de prédiction : {e}")
        logger.error(f"Erreur de prédiction : {e}")
    
    except Exception as e:
        st.error("❌ Une erreur inattendue s'est produite. Veuillez contacter l'administrateur.")
        logger.error(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    main()
