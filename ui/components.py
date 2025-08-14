"""
Composants d'interface utilisateur réutilisables.
"""
import streamlit as st
from typing import Dict, Any

from config.constants import (
    Gender, Country, Category, BinaryChoice, VALIDATION_RANGES
)


class InputComponents:
    """Classe contenant les composants d'entrée Streamlit."""
    
    @staticmethod
    def render_numeric_input(
        label: str, 
        field_name: str, 
        help_text: str = None
    ) -> float:
        """
        Affiche un input numérique avec validation.
        
        Args:
            label: Label affiché
            field_name: Nom du champ pour la validation
            help_text: Texte d'aide optionnel
            
        Returns:
            Valeur saisie
        """
        config = VALIDATION_RANGES[field_name]
        
        if field_name in ["balance", "estimated_salary"]:
            return st.number_input(
                label,
                min_value=config["min"],
                max_value=config["max"],
                value=config["default"],
                step=1000.0,
                help=help_text
            )
        else:
            return st.number_input(
                label,
                min_value=int(config["min"]),
                max_value=int(config["max"]),
                value=int(config["default"]),
                help=help_text
            )
    
    @staticmethod
    def render_slider_input(
        label: str, 
        field_name: str, 
        help_text: str = None
    ) -> int:
        """
        Affiche un slider avec validation.
        
        Args:
            label: Label affiché
            field_name: Nom du champ pour la validation
            help_text: Texte d'aide optionnel
            
        Returns:
            Valeur sélectionnée
        """
        config = VALIDATION_RANGES[field_name]
        
        return st.slider(
            label,
            min_value=int(config["min"]),
            max_value=int(config["max"]),
            value=int(config["default"]),
            help=help_text
        )
    
    @staticmethod
    def render_selectbox(
        label: str, 
        enum_class, 
        help_text: str = None
    ):
        """
        Affiche une selectbox pour une énumération.
        
        Args:
            label: Label affiché
            enum_class: Classe d'énumération
            help_text: Texte d'aide optionnel
            
        Returns:
            Valeur sélectionnée
        """
        options = [e.value for e in enum_class]
        selected_value = st.selectbox(label, options, help=help_text)
        
        # Retourne l'enum correspondant
        for enum_item in enum_class:
            if enum_item.value == selected_value:
                return enum_item
        
        return list(enum_class)[0]  # Fallback


class DisplayComponents:
    """Classe contenant les composants d'affichage."""
    
    @staticmethod
    def render_prediction_result(result, customer_data):
        """
        Affiche le résultat de prédiction de manière formatée.
        
        Args:
            result: Résultat de la prédiction
            customer_data: Données du client
        """
        # Conteneur principal
        st.markdown("---")
        st.subheader("🎯 Résultat de la Prédiction")
        
        # Colonnes pour l'affichage
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if result.will_churn:
                st.error(f"⚠️ **Risque de Départ**")
            else:
                st.success(f"✅ **Client Fidèle**")
        
        with col2:
            st.metric(
                "Probabilité de Churn",
                result.formatted_probability,
                delta=None
            )
        
        with col3:
            risk_color = {
                "Faible": "🟢",
                "Moyen": "🟡", 
                "Élevé": "🔴"
            }
            st.metric(
                "Niveau de Risque",
                f"{risk_color.get(result.risk_level, '⚪')} {result.risk_level}"
            )
        
        # Message détaillé
        st.markdown("### 💬 Interprétation")
        if result.will_churn:
            st.warning(
                f"Ce client présente un **risque {result.risk_level.lower()}** de churn "
                f"avec une probabilité de {result.formatted_probability}. "
                f"Il est recommandé de mettre en place des actions de rétention."
            )
        else:
            st.info(
                f"Ce client a une **faible probabilité** de churn "
                f"({result.formatted_probability}). Il s'agit d'un client fidèle "
                f"avec un risque {result.risk_level.lower()}."
            )
    
    @staticmethod
    def render_customer_summary(customer_data):
        """
        Affiche un résumé des données client.
        
        Args:
            customer_data: Données du client
        """
        st.subheader("👤 Profil Client")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Informations Démographiques**")
            st.write(f"• Âge : {customer_data.age} ans")
            st.write(f"• Sexe : {customer_data.gender.value}")
            st.write(f"• Pays : {customer_data.country.value}")
            st.write(f"• Catégorie : {customer_data.category.value}")
        
        with col2:
            st.write("**Informations Financières**")
            st.write(f"• Score de crédit : {customer_data.credit_score}")
            st.write(f"• Solde : {customer_data.balance:,.0f} €")
            st.write(f"• Salaire estimé : {customer_data.estimated_salary:,.0f} €")
            st.write(f"• Nombre de produits : {customer_data.num_of_products}")
    
    @staticmethod
    def render_error_message(errors: list):
        """
        Affiche les messages d'erreur de validation.
        
        Args:
            errors: Liste des erreurs
        """
        if errors:
            st.error("❌ **Erreurs de validation détectées :**")
            for error in errors:
                st.error(f"• {error}")
            return True
        return False
