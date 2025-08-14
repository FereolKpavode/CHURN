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
from ui.pages import PredictionPage, AnalyticsPage
from ui.batch_processing import BatchProcessor
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



def main():
    """Fonction principale de l'application."""
    # Configuration de la page
    configure_page()
    
    # Titre principal
    st.title(Settings.APP_TITLE)
    
    # Barre latérale
    render_sidebar()
    
    # Navigation par onglets
    tab1, tab2, tab3 = st.tabs(["🎯 Prédiction", "📊 Traitement par Lots", "📈 Analytics"])
    
    with tab1:
        try:
            PredictionPage.render()
        except ChurnPredictionError as e:
            st.error(f"❌ Erreur de prédiction : {e}")
            logger.error(f"Erreur de prédiction : {e}")
        except Exception as e:
            st.error("❌ Une erreur inattendue s'est produite. Veuillez contacter l'administrateur.")
            logger.error(f"Erreur inattendue : {e}")
    
    with tab2:
        try:
            BatchProcessor.render_batch_page()
        except Exception as e:
            st.error("❌ Erreur lors du traitement par lots.")
            logger.error(f"Erreur batch processing : {e}")
    
    with tab3:
        try:
            AnalyticsPage.render()
        except Exception as e:
            st.error("❌ Erreur lors du chargement des analytics.")
            logger.error(f"Erreur analytics : {e}")


if __name__ == "__main__":
    main()
