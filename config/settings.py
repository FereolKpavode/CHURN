"""
Configuration centralisée de l'application.
"""
import os
from pathlib import Path


class Settings:
    """Classe de configuration de l'application."""
    
    # Chemins
    BASE_DIR = Path(__file__).parent.parent
    MODEL_PATH = BASE_DIR / "models" / "random_forest_model.pkl"
    
    # Configuration Streamlit
    APP_TITLE = "Prédiction de l'attrition des clients (Churn)"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
    
    # Configuration du modèle
    MODEL_CACHE_TTL = 3600  # 1 heure en secondes
    
    # Messages
    MESSAGES = {
        "churn_risk": "⚠️ Le client est susceptible de **partir**. Probabilité : {prob:.2%}",
        "no_churn_risk": "✅ Le client est susceptible de **rester**. Probabilité de churn : {prob:.2%}",
        "model_error": "❌ Erreur lors du chargement du modèle. Veuillez contacter l'administrateur.",
        "prediction_error": "❌ Erreur lors de la prédiction. Vérifiez vos données d'entrée."
    }
    
    @classmethod
    def get_model_path(cls) -> str:
        """Retourne le chemin vers le modèle."""
        return str(cls.MODEL_PATH)
