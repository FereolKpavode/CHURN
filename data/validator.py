"""
Validation des données pour l'application de prédiction de churn.
"""
from typing import Dict, Any, List

from config.constants import VALIDATION_RANGES, Gender, Country, Category, BinaryChoice
from utils.exceptions import DataValidationError


class DataValidator:
    """Classe pour valider les données d'entrée."""
    
    @staticmethod
    def validate_numeric_field(value: float, field_name: str) -> None:
        """Valide un champ numérique."""
        if field_name not in VALIDATION_RANGES:
            raise DataValidationError(f"Champ inconnu : {field_name}")
        
        ranges = VALIDATION_RANGES[field_name]
        if not (ranges["min"] <= value <= ranges["max"]):
            raise DataValidationError(
                f"{field_name} doit être entre {ranges['min']} et {ranges['max']}, "
                f"reçu : {value}"
            )
    
    @staticmethod
    def validate_enum_field(value: Any, enum_class, field_name: str) -> None:
        """Valide un champ d'énumération."""
        if value not in enum_class:
            valid_values = [e.value for e in enum_class]
            raise DataValidationError(
                f"{field_name} doit être l'une des valeurs : {valid_values}, "
                f"reçu : {value}"
            )
    
    @classmethod
    def validate_customer_data(cls, data: Dict[str, Any]) -> List[str]:
        """
        Valide toutes les données client.
        
        Returns:
            Liste des erreurs de validation (vide si tout est valide)
        """
        errors = []
        
        try:
            # Validation des champs numériques
            numeric_fields = {
                'credit_score': data.get('credit_score'),
                'age': data.get('age'),
                'tenure': data.get('tenure'),
                'balance': data.get('balance'),
                'num_of_products': data.get('num_of_products'),
                'estimated_salary': data.get('estimated_salary'),
                'satisfaction_score': data.get('satisfaction_score'),
                'point_earned': data.get('point_earned')
            }
            
            for field, value in numeric_fields.items():
                if value is None:
                    errors.append(f"Le champ {field} est requis")
                    continue
                
                try:
                    cls.validate_numeric_field(value, field)
                except DataValidationError as e:
                    errors.append(str(e))
            
            # Validation des champs d'énumération
            enum_validations = [
                (data.get('gender'), Gender, 'gender'),
                (data.get('country'), Country, 'country'),
                (data.get('category'), Category, 'category'),
                (data.get('has_credit_card'), BinaryChoice, 'has_credit_card'),
                (data.get('is_active_member'), BinaryChoice, 'is_active_member'),
                (data.get('complain'), BinaryChoice, 'complain')
            ]
            
            for value, enum_class, field_name in enum_validations:
                if value is None:
                    errors.append(f"Le champ {field_name} est requis")
                    continue
                
                try:
                    cls.validate_enum_field(value, enum_class, field_name)
                except DataValidationError as e:
                    errors.append(str(e))
        
        except Exception as e:
            errors.append(f"Erreur de validation inattendue : {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_business_rules(data: Dict[str, Any]) -> List[str]:
        """
        Valide les règles métier.
        
        Returns:
            Liste des erreurs de règles métier
        """
        errors = []
        
        # Règle : Un client très jeune ne peut pas avoir un salaire très élevé
        if data.get('age', 0) < 25 and data.get('estimated_salary', 0) > 150000:
            errors.append("Incohérence : âge trop jeune pour un salaire si élevé")
        
        # Règle : Un client avec un mauvais score de crédit ne devrait pas avoir un solde très élevé
        if data.get('credit_score', 0) < 400 and data.get('balance', 0) > 200000:
            errors.append("Incohérence : score de crédit trop bas pour un solde si élevé")
        
        # Règle : Un client avec 4 produits devrait être un membre actif
        if (data.get('num_of_products', 0) >= 4 and 
            data.get('is_active_member') == BinaryChoice.NO):
            errors.append("Incohérence : client avec 4 produits mais non actif")
        
        return errors
