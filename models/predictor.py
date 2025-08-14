"""
Classe de prédiction pour l'application de churn.
"""
import joblib
import pandas as pd
import streamlit as st
from typing import Optional
import logging

from config.settings import Settings
from config.constants import MODEL_FEATURES
from data.schemas import CustomerData, PredictionResult
from utils.exceptions import ModelLoadError, PredictionError

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChurnPredictor:
    """Classe responsable de la prédiction de churn."""
    
    def __init__(self):
        """Initialise le prédicteur."""
        self.model = None
        self._load_model()
    
    @st.cache_resource
    def _load_model(_self):
        """
        Charge le modèle de machine learning avec mise en cache.
        
        Note: Le paramètre _self est nécessaire pour st.cache_resource
        """
        try:
            logger.info(f"Chargement du modèle depuis {Settings.get_model_path()}")
            model = joblib.load(Settings.get_model_path())
            logger.info("Modèle chargé avec succès")
            return model
        except FileNotFoundError:
            logger.error(f"Fichier modèle non trouvé : {Settings.get_model_path()}")
            raise ModelLoadError(f"Modèle non trouvé : {Settings.get_model_path()}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle : {e}")
            raise ModelLoadError(f"Erreur de chargement du modèle : {e}")
    
    def predict(self, customer_data: CustomerData) -> PredictionResult:
        """
        Effectue une prédiction de churn.
        
        Args:
            customer_data: Données du client
            
        Returns:
            Résultat de la prédiction
            
        Raises:
            PredictionError: En cas d'erreur lors de la prédiction
        """
        try:
            # Chargement du modèle si nécessaire
            if self.model is None:
                self.model = self._load_model()
            
            # Conversion en DataFrame
            data_dict = customer_data.to_dict()
            input_df = pd.DataFrame([data_dict])
            
            # Vérification que toutes les colonnes requises sont présentes
            missing_features = set(MODEL_FEATURES) - set(input_df.columns)
            if missing_features:
                raise PredictionError(f"Caractéristiques manquantes : {missing_features}")
            
            # Réorganisation des colonnes dans l'ordre attendu
            input_df = input_df[MODEL_FEATURES]
            
            # Prédiction
            prediction = self.model.predict(input_df)[0]
            probability = self.model.predict_proba(input_df)[0][1]  # Probabilité de churn
            
            # Détermination du niveau de risque
            risk_level = self._get_risk_level(probability)
            
            logger.info(f"Prédiction effectuée : {prediction}, probabilité : {probability:.3f}")
            
            return PredictionResult(
                prediction=int(prediction),
                probability=float(probability),
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction : {e}")
            raise PredictionError(f"Erreur de prédiction : {e}")
    
    @staticmethod
    def _get_risk_level(probability: float) -> str:
        """
        Détermine le niveau de risque basé sur la probabilité.
        
        Args:
            probability: Probabilité de churn
            
        Returns:
            Niveau de risque
        """
        if probability < 0.3:
            return "Faible"
        elif probability < 0.7:
            return "Moyen"
        else:
            return "Élevé"
    
    def get_model_info(self) -> dict:
        """
        Retourne les informations du modèle.
        
        Returns:
            Dictionnaire avec les informations du modèle
        """
        if self.model is None:
            self.model = self._load_model()
            
        return {
            "type": type(self.model).__name__,
            "features": MODEL_FEATURES,
            "n_features": len(MODEL_FEATURES)
        }
