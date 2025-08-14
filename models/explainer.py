"""
Module d'explainability avec SHAP values pour l'application de churn.
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

try:
    import shap
    import matplotlib.pyplot as plt
    import seaborn as sns
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from data.schemas import CustomerData, PredictionResult
from models.predictor import ChurnPredictor
from config.constants import MODEL_FEATURES
from utils.exceptions import ChurnPredictionError

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """Classe pour l'explainability avec SHAP values."""
    
    def __init__(self):
        """Initialise l'explainer SHAP."""
        self.explainer = None
        self.background_data = None
        self.predictor = ChurnPredictor()
        
        if not SHAP_AVAILABLE:
            logger.warning("SHAP non disponible. Installer avec: pip install shap")
            st.warning(
                "⚠️ **SHAP non disponible**: La bibliothèque SHAP n'est pas installée. "
                "Exécutez `pip install shap matplotlib seaborn` pour activer l'explainability."
            )
    
    @st.cache_resource
    def _initialize_explainer(_self):
        """
        Initialise l'explainer SHAP avec mise en cache.
        
        Note: Le paramètre _self est nécessaire pour st.cache_resource
        """
        if not SHAP_AVAILABLE:
            return None, None
        
        try:
            logger.info("Initialisation de l'explainer SHAP...")
            
            # Génération de données synthétiques pour le background
            background_data = _self._generate_background_data()
            
            # Création de l'explainer
            explainer = shap.Explainer(
                _self.predictor.model.predict_proba,
                background_data,
                feature_names=MODEL_FEATURES
            )
            
            logger.info("Explainer SHAP initialisé avec succès")
            return explainer, background_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation SHAP : {e}")
            return None, None
    
    def _generate_background_data(self) -> pd.DataFrame:
        """Génère des données de background pour SHAP."""
        np.random.seed(42)
        
        # Génération de données synthétiques représentatives
        n_samples = 100
        
        background_data = {
            'creditscore': np.random.normal(650, 100, n_samples).clip(300, 900),
            'age': np.random.normal(40, 15, n_samples).clip(18, 100),
            'tenure': np.random.exponential(5, n_samples).clip(0, 20),
            'balance': np.random.lognormal(10, 1, n_samples).clip(0, 300000),
            'numofproducts': np.random.choice([1, 2, 3, 4], n_samples, p=[0.3, 0.4, 0.2, 0.1]),
            'hascrcard': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
            'isactivemember': np.random.choice([0, 1], n_samples, p=[0.2, 0.8]),
            'estimatedsalary': np.random.normal(75000, 25000, n_samples).clip(0, 300000),
            'complain': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'satisfaction score': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.1, 0.3, 0.3, 0.2]),
            'point earned': np.random.exponential(1000, n_samples).clip(0, 100000),
            'Male': np.random.choice([0, 1], n_samples, p=[0.5, 0.5]),
            'Germany': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'Spain': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'GOLD': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'PLATINUM': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'SILVER': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        }
        
        df = pd.DataFrame(background_data)
        
        # Assurer la cohérence des variables catégorielles
        for i in range(len(df)):
            # Un seul pays peut être sélectionné
            if df.loc[i, 'Germany'] == 1:
                df.loc[i, 'Spain'] = 0
            elif df.loc[i, 'Spain'] == 1:
                df.loc[i, 'Germany'] = 0
            
            # Une seule catégorie peut être sélectionnée
            if df.loc[i, 'PLATINUM'] == 1:
                df.loc[i, ['GOLD', 'SILVER']] = 0
            elif df.loc[i, 'GOLD'] == 1:
                df.loc[i, 'SILVER'] = 0
        
        return df[MODEL_FEATURES]
    
    def get_shap_explanation(self, customer_data: CustomerData) -> Optional[Dict]:
        """
        Calcule les SHAP values pour un client.
        
        Args:
            customer_data: Données du client
            
        Returns:
            Dictionnaire contenant les SHAP values et métadonnées
        """
        if not SHAP_AVAILABLE:
            return None
        
        try:
            # Initialisation de l'explainer si nécessaire
            if self.explainer is None:
                self.explainer, self.background_data = self._initialize_explainer()
            
            if self.explainer is None:
                return None
            
            # Conversion des données client
            data_dict = customer_data.to_dict()
            input_df = pd.DataFrame([data_dict])[MODEL_FEATURES]
            
            # Calcul des SHAP values
            shap_values = self.explainer(input_df)
            
            # Prédiction de base (average prediction)
            base_value = self.explainer.expected_value[1]  # Pour la classe churn
            
            # Valeurs SHAP pour ce client
            instance_shap_values = shap_values.values[0, :, 1]  # Classe churn
            
            # Création du dictionnaire de résultats
            shap_dict = {
                'base_value': float(base_value),
                'shap_values': dict(zip(MODEL_FEATURES, instance_shap_values.tolist())),
                'feature_values': dict(zip(MODEL_FEATURES, input_df.iloc[0].tolist())),
                'prediction': float(shap_values.base_values[0] + instance_shap_values.sum())
            }
            
            logger.info("SHAP values calculées avec succès")
            return shap_dict
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul SHAP : {e}")
            return None
    
    def get_feature_importance_comparison(self) -> Optional[Dict]:
        """
        Compare l'importance globale vs SHAP pour les features.
        
        Returns:
            Dictionnaire avec comparaison des importances
        """
        if not SHAP_AVAILABLE:
            return None
        
        try:
            # Importance du modèle Random Forest
            model_importance = dict(zip(
                MODEL_FEATURES,
                self.predictor.model.feature_importances_
            ))
            
            # SHAP importance moyenne (simulée pour demo)
            # En production, ceci serait calculé sur un échantillon de données
            if self.explainer is None:
                self.explainer, self.background_data = self._initialize_explainer()
            
            if self.explainer is None:
                return None
            
            # Calcul SHAP sur échantillon de background
            sample_shap = self.explainer(self.background_data.sample(20))
            shap_importance = np.abs(sample_shap.values[:, :, 1]).mean(axis=0)
            
            shap_importance_dict = dict(zip(MODEL_FEATURES, shap_importance))
            
            return {
                'model_importance': model_importance,
                'shap_importance': shap_importance_dict
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison d'importance : {e}")
            return None
    
    @staticmethod
    def interpret_shap_values(shap_dict: Dict) -> Dict[str, str]:
        """
        Interprète les SHAP values en language naturel.
        
        Args:
            shap_dict: Dictionnaire des SHAP values
            
        Returns:
            Dictionnaire avec interprétations textuelles
        """
        if not shap_dict:
            return {}
        
        interpretations = {}
        shap_values = shap_dict['shap_values']
        feature_values = shap_dict['feature_values']
        
        # Tri par impact absolu
        sorted_features = sorted(
            shap_values.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        # Interprétation des top 5 features
        for i, (feature, shap_val) in enumerate(sorted_features[:5]):
            feature_val = feature_values[feature]
            impact = "augmente" if shap_val > 0 else "diminue"
            magnitude = "fortement" if abs(shap_val) > 0.1 else "modérément"
            
            # Interprétations spécifiques par feature
            if feature == 'age':
                interpretations[feature] = f"L'âge ({feature_val} ans) {magnitude} {impact} le risque de churn"
            elif feature == 'creditscore':
                interpretations[feature] = f"Le score de crédit ({feature_val}) {magnitude} {impact} le risque de churn"
            elif feature == 'satisfaction score':
                interpretations[feature] = f"Le score de satisfaction ({feature_val}/5) {magnitude} {impact} le risque de churn"
            elif feature == 'numofproducts':
                interpretations[feature] = f"Le nombre de produits ({feature_val}) {magnitude} {impact} le risque de churn"
            elif feature == 'balance':
                interpretations[feature] = f"Le solde ({feature_val:,.0f}€) {magnitude} {impact} le risque de churn"
            else:
                interpretations[feature] = f"{feature} ({feature_val}) {magnitude} {impact} le risque de churn"
        
        return interpretations


class ModelMonitor:
    """Classe pour le monitoring avancé du modèle."""
    
    def __init__(self):
        """Initialise le monitor."""
        self.predictor = ChurnPredictor()
    
    @staticmethod
    def simulate_model_performance() -> Dict:
        """
        Simule les métriques de performance du modèle.
        
        Returns:
            Dictionnaire avec métriques simulées
        """
        # En production, ces métriques seraient calculées sur de vraies données
        np.random.seed(42)
        
        # Simulation de 30 jours de données
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
        
        # Métriques avec tendance réaliste
        base_accuracy = 0.85
        base_precision = 0.72
        base_recall = 0.68
        base_f1 = 0.70
        
        metrics = {
            'dates': dates.strftime('%Y-%m-%d').tolist(),
            'accuracy': [base_accuracy + np.random.normal(0, 0.02) for _ in range(30)],
            'precision': [base_precision + np.random.normal(0, 0.03) for _ in range(30)],
            'recall': [base_recall + np.random.normal(0, 0.025) for _ in range(30)],
            'f1_score': [base_f1 + np.random.normal(0, 0.02) for _ in range(30)],
            'prediction_volume': [np.random.poisson(50) + 20 for _ in range(30)],
            'churn_rate': [0.125 + np.random.normal(0, 0.01) for _ in range(30)]
        }
        
        # Ajout d'une tendance légère
        trend = np.linspace(0, -0.01, 30)
        metrics['accuracy'] = [max(0.7, acc + t) for acc, t in zip(metrics['accuracy'], trend)]
        
        return metrics
    
    @staticmethod
    def detect_data_drift() -> Dict:
        """
        Simule la détection de dérive des données.
        
        Returns:
            Dictionnaire avec alertes de drift
        """
        np.random.seed(42)
        
        features_drift = {
            'creditscore': {'drift_score': 0.12, 'status': 'OK', 'threshold': 0.15},
            'age': {'drift_score': 0.08, 'status': 'OK', 'threshold': 0.15},
            'balance': {'drift_score': 0.18, 'status': 'ALERT', 'threshold': 0.15},
            'satisfaction score': {'drift_score': 0.22, 'status': 'CRITICAL', 'threshold': 0.15},
            'numofproducts': {'drift_score': 0.05, 'status': 'OK', 'threshold': 0.15}
        }
        
        return features_drift
    
    @staticmethod
    def get_prediction_trends() -> Dict:
        """
        Analyse les tendances de prédiction.
        
        Returns:
            Dictionnaire avec tendances
        """
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
        
        # Simulation de tendances réalistes
        base_churn_rate = 0.125
        seasonal_effect = np.sin(np.arange(30) * 2 * np.pi / 30) * 0.02
        trend_effect = np.linspace(0, 0.01, 30)
        noise = np.random.normal(0, 0.005, 30)
        
        churn_rates = base_churn_rate + seasonal_effect + trend_effect + noise
        churn_rates = np.clip(churn_rates, 0.05, 0.25)
        
        return {
            'dates': dates.strftime('%Y-%m-%d').tolist(),
            'daily_churn_rate': churn_rates.tolist(),
            'daily_predictions': [np.random.poisson(45) + 25 for _ in range(30)],
            'high_risk_clients': [int(pred * rate * 0.7) for pred, rate in zip(
                [np.random.poisson(45) + 25 for _ in range(30)], churn_rates
            )]
        }


class AlertSystem:
    """Système d'alertes pour le monitoring."""
    
    @staticmethod
    def check_alerts(performance_data: Dict, drift_data: Dict) -> List[Dict]:
        """
        Vérifie et génère les alertes système.
        
        Args:
            performance_data: Données de performance
            drift_data: Données de dérive
            
        Returns:
            Liste des alertes actives
        """
        alerts = []
        
        # Alerte performance
        current_accuracy = performance_data['accuracy'][-1]
        if current_accuracy < 0.80:
            alerts.append({
                'type': 'PERFORMANCE',
                'level': 'CRITICAL' if current_accuracy < 0.75 else 'WARNING',
                'message': f"Précision du modèle en baisse : {current_accuracy:.2%}",
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                'action': "Réévaluer le modèle et considérer un retraining"
            })
        
        # Alertes de dérive
        for feature, drift_info in drift_data.items():
            if drift_info['status'] == 'CRITICAL':
                alerts.append({
                    'type': 'DATA_DRIFT',
                    'level': 'CRITICAL',
                    'message': f"Dérive critique détectée sur {feature} (score: {drift_info['drift_score']:.2f})",
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                    'action': "Investiguer les changements dans la distribution des données"
                })
            elif drift_info['status'] == 'ALERT':
                alerts.append({
                    'type': 'DATA_DRIFT',
                    'level': 'WARNING',
                    'message': f"Dérive détectée sur {feature} (score: {drift_info['drift_score']:.2f})",
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                    'action': "Surveiller l'évolution de cette variable"
                })
        
        # Alerte volume de prédictions
        recent_volume = performance_data['prediction_volume'][-7:]  # 7 derniers jours
        avg_volume = np.mean(recent_volume)
        if avg_volume < 20:
            alerts.append({
                'type': 'VOLUME',
                'level': 'WARNING',
                'message': f"Volume de prédictions faible : {avg_volume:.0f}/jour",
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                'action': "Vérifier l'utilisation du système par les utilisateurs"
            })
        
        return alerts
    
    @staticmethod
    def get_client_risk_alerts() -> List[Dict]:
        """
        Génère des alertes pour les clients à très haut risque.
        
        Returns:
            Liste des clients nécessitant une action immédiate
        """
        # Simulation de clients à haut risque
        high_risk_clients = [
            {
                'client_id': 'C001245',
                'name': 'Client Anonyme A',
                'churn_probability': 0.92,
                'risk_factors': ['Satisfaction très faible (1/5)', 'Plainte récente', 'Solde en baisse'],
                'last_prediction': '2024-01-15 14:30',
                'recommended_action': 'Contact immédiat par manager'
            },
            {
                'client_id': 'C002847',
                'name': 'Client Anonyme B', 
                'churn_probability': 0.87,
                'risk_factors': ['Âge jeune + salaire élevé', 'Un seul produit', 'Membre inactif'],
                'last_prediction': '2024-01-15 11:15',
                'recommended_action': 'Proposition produits premium'
            },
            {
                'client_id': 'C003156',
                'name': 'Client Anonyme C',
                'churn_probability': 0.84,
                'risk_factors': ['Score crédit faible', 'Solde très bas', 'Satisfaction modérée'],
                'last_prediction': '2024-01-15 09:45',
                'recommended_action': 'Accompagnement financier personnalisé'
            }
        ]
        
        return high_risk_clients
