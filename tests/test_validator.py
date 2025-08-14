"""
Tests unitaires pour le module de validation des données.
"""
import unittest
from config.constants import Gender, Country, Category, BinaryChoice
from data.validator import DataValidator
from utils.exceptions import DataValidationError


class TestDataValidator(unittest.TestCase):
    """Tests pour la classe DataValidator."""
    
    def setUp(self):
        """Configuration des tests."""
        self.valid_data = {
            'credit_score': 650,
            'age': 35,
            'tenure': 5,
            'balance': 50000.0,
            'num_of_products': 2,
            'estimated_salary': 75000.0,
            'satisfaction_score': 4,
            'point_earned': 1000,
            'has_credit_card': BinaryChoice.YES,
            'is_active_member': BinaryChoice.YES,
            'complain': BinaryChoice.NO,
            'gender': Gender.MALE,
            'country': Country.FRANCE,
            'category': Category.SILVER
        }
    
    def test_validate_numeric_field_valid(self):
        """Test de validation d'un champ numérique valide."""
        try:
            DataValidator.validate_numeric_field(650, 'credit_score')
        except DataValidationError:
            self.fail("La validation a échoué pour une valeur valide")
    
    def test_validate_numeric_field_invalid_range(self):
        """Test de validation d'un champ numérique hors limites."""
        with self.assertRaises(DataValidationError):
            DataValidator.validate_numeric_field(200, 'credit_score')  # Trop bas
        
        with self.assertRaises(DataValidationError):
            DataValidator.validate_numeric_field(1000, 'credit_score')  # Trop haut
    
    def test_validate_enum_field_valid(self):
        """Test de validation d'un champ d'énumération valide."""
        try:
            DataValidator.validate_enum_field(Gender.MALE, Gender, 'gender')
        except DataValidationError:
            self.fail("La validation a échoué pour une valeur valide")
    
    def test_validate_customer_data_valid(self):
        """Test de validation complète avec des données valides."""
        errors = DataValidator.validate_customer_data(self.valid_data)
        self.assertEqual(len(errors), 0, f"Erreurs inattendues : {errors}")
    
    def test_validate_customer_data_missing_field(self):
        """Test avec un champ manquant."""
        invalid_data = self.valid_data.copy()
        del invalid_data['credit_score']
        
        errors = DataValidator.validate_customer_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('credit_score' in error for error in errors))
    
    def test_validate_business_rules_young_high_salary(self):
        """Test de règle métier : jeune avec salaire élevé."""
        data = self.valid_data.copy()
        data['age'] = 22
        data['estimated_salary'] = 200000
        
        errors = DataValidator.validate_business_rules(data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('âge trop jeune' in error for error in errors))
    
    def test_validate_business_rules_low_credit_high_balance(self):
        """Test de règle métier : mauvais crédit avec solde élevé."""
        data = self.valid_data.copy()
        data['credit_score'] = 350
        data['balance'] = 250000
        
        errors = DataValidator.validate_business_rules(data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('score de crédit' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
