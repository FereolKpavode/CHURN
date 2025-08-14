"""
Constantes et énumérations pour l'application de prédiction de churn.
"""
from enum import Enum
from typing import Dict, List


class Gender(Enum):
    """Énumération pour les genres."""
    MALE = "Homme"
    FEMALE = "Femme"


class Country(Enum):
    """Énumération pour les pays."""
    FRANCE = "France"
    GERMANY = "Allemagne"
    SPAIN = "Espagne"


class Category(Enum):
    """Énumération pour les catégories de clients."""
    RUBIS = "RUBIS"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class BinaryChoice(Enum):
    """Énumération pour les choix binaires."""
    YES = "Oui"
    NO = "Non"


# Constantes de validation
VALIDATION_RANGES: Dict[str, Dict[str, float]] = {
    "credit_score": {"min": 300, "max": 900, "default": 600},
    "age": {"min": 18, "max": 100, "default": 30},
    "tenure": {"min": 0, "max": 20, "default": 3},
    "balance": {"min": 0.0, "max": 300000.0, "default": 1000.0},
    "num_of_products": {"min": 1, "max": 4, "default": 2},
    "estimated_salary": {"min": 0.0, "max": 300000.0, "default": 50000.0},
    "satisfaction_score": {"min": 0, "max": 5, "default": 3},
    "point_earned": {"min": 0, "max": 100000, "default": 500}
}

# Colonnes du modèle (ordre important - EXACTEMENT comme dans le modèle original)
MODEL_FEATURES: List[str] = [
    "creditscore",
    "age", 
    "tenure",
    "balance",
    "numofproducts",
    "hascrcard",
    "isactivemember",
    "estimatedsalary",
    "complain",
    "satisfaction score",  # ATTENTION: avec espace comme dans le modèle original
    "point earned",       # ATTENTION: avec espace comme dans le modèle original
    "Male",
    "Germany",
    "Spain",
    "GOLD",
    "PLATINUM",
    "SILVER"
]
