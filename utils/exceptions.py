"""
Exceptions personnalisées pour l'application de prédiction de churn.
"""


class ChurnPredictionError(Exception):
    """Exception de base pour les erreurs de prédiction de churn."""
    pass


class ModelLoadError(ChurnPredictionError):
    """Erreur lors du chargement du modèle."""
    pass


class DataValidationError(ChurnPredictionError):
    """Erreur de validation des données."""
    pass


class PredictionError(ChurnPredictionError):
    """Erreur lors de la prédiction."""
    pass


class EncodingError(ChurnPredictionError):
    """Erreur lors de l'encodage des données."""
    pass
