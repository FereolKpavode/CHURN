"""
Schémas de données pour l'application de prédiction de churn.
"""
from dataclasses import dataclass
from typing import Optional

from config.constants import Gender, Country, Category, BinaryChoice


@dataclass
class CustomerData:
    """Schéma des données client."""
    
    # Données numériques
    credit_score: int
    age: int
    tenure: int
    balance: float
    num_of_products: int
    estimated_salary: float
    satisfaction_score: int
    point_earned: int
    
    # Données binaires
    has_credit_card: BinaryChoice
    is_active_member: BinaryChoice
    complain: BinaryChoice
    
    # Données catégorielles
    gender: Gender
    country: Country
    category: Category
    
    def to_dict(self) -> dict:
        """Convertit les données en dictionnaire avec les noms de colonnes attendus par le modèle."""
        return {
            'creditscore': self.credit_score,
            'age': self.age,
            'tenure': self.tenure,
            'balance': self.balance,
            'numofproducts': self.num_of_products,
            'hascrcard': 1 if self.has_credit_card == BinaryChoice.YES else 0,
            'isactivemember': 1 if self.is_active_member == BinaryChoice.YES else 0,
            'estimatedsalary': self.estimated_salary,
            'complain': 1 if self.complain == BinaryChoice.YES else 0,
            'satisfaction score': self.satisfaction_score,  # AVEC espace pour correspondre au modèle
            'point earned': self.point_earned,              # AVEC espace pour correspondre au modèle
            'Male': 1 if self.gender == Gender.MALE else 0,
            'Germany': 1 if self.country == Country.GERMANY else 0,
            'Spain': 1 if self.country == Country.SPAIN else 0,
            'GOLD': 1 if self.category == Category.GOLD else 0,
            'PLATINUM': 1 if self.category == Category.PLATINUM else 0,
            'SILVER': 1 if self.category == Category.SILVER else 0
        }


@dataclass
class PredictionResult:
    """Schéma du résultat de prédiction."""
    
    prediction: int  # 0 = reste, 1 = part
    probability: float  # Probabilité de churn
    risk_level: str  # "Faible", "Moyen", "Élevé"
    
    @property
    def will_churn(self) -> bool:
        """Indique si le client va partir."""
        return self.prediction == 1
    
    @property
    def formatted_probability(self) -> str:
        """Probabilité formatée en pourcentage."""
        return f"{self.probability:.2%}"
