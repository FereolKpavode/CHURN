"""
Composants de visualisation pour l'application de churn.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import numpy as np

from data.schemas import CustomerData, PredictionResult
from config.constants import VALIDATION_RANGES


class VisualizationComponents:
    """Classe contenant les composants de visualisation."""
    
    @staticmethod
    def render_customer_profile_radar(customer_data: CustomerData):
        """
        Affiche un graphique radar du profil client.
        
        Args:
            customer_data: Données du client
        """
        st.subheader("🎯 Profil Client - Vue Radar")
        
        # Normalisation des valeurs entre 0 et 1
        normalized_values = []
        categories = []
        
        # Score de crédit (normalisé sur 300-900)
        credit_norm = (customer_data.credit_score - 300) / (900 - 300)
        normalized_values.append(credit_norm)
        categories.append("Score Crédit")
        
        # Âge (normalisé sur 18-100)
        age_norm = (customer_data.age - 18) / (100 - 18)
        normalized_values.append(age_norm)
        categories.append("Âge")
        
        # Solde (normalisé sur échelle log)
        balance_norm = min(customer_data.balance / 200000, 1.0)
        normalized_values.append(balance_norm)
        categories.append("Solde")
        
        # Salaire (normalisé sur échelle log)
        salary_norm = min(customer_data.estimated_salary / 200000, 1.0)
        normalized_values.append(salary_norm)
        categories.append("Salaire")
        
        # Ancienneté
        tenure_norm = customer_data.tenure / 20
        normalized_values.append(tenure_norm)
        categories.append("Ancienneté")
        
        # Score de satisfaction
        satisfaction_norm = customer_data.satisfaction_score / 5
        normalized_values.append(satisfaction_norm)
        categories.append("Satisfaction")
        
        # Nombre de produits
        products_norm = customer_data.num_of_products / 4
        normalized_values.append(products_norm)
        categories.append("Nb Produits")
        
        # Fermer le radar
        normalized_values.append(normalized_values[0])
        categories.append(categories[0])
        
        # Création du graphique radar
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name='Profil Client',
            line_color='rgb(32, 201, 151)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_risk_distribution():
        """Affiche la distribution des niveaux de risque (données simulées)."""
        st.subheader("📊 Distribution des Risques - Base Clients")
        
        # Données simulées pour la démonstration
        risk_data = {
            'Niveau de Risque': ['Faible', 'Moyen', 'Élevé'],
            'Pourcentage': [65, 25, 10],
            'Nombre de Clients': [6500, 2500, 1000]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique en camembert
            fig_pie = px.pie(
                values=risk_data['Pourcentage'],
                names=risk_data['Niveau de Risque'],
                title="Répartition par Niveau de Risque",
                color_discrete_map={
                    'Faible': '#32c997',
                    'Moyen': '#ffc107', 
                    'Élevé': '#dc3545'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Graphique en barres
            fig_bar = px.bar(
                x=risk_data['Niveau de Risque'],
                y=risk_data['Nombre de Clients'],
                title="Nombre de Clients par Risque",
                color=risk_data['Niveau de Risque'],
                color_discrete_map={
                    'Faible': '#32c997',
                    'Moyen': '#ffc107',
                    'Élevé': '#dc3545'
                }
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    @staticmethod
    def render_feature_importance(model_info: Dict[str, Any]):
        """
        Affiche l'importance des features (simulée pour Random Forest).
        
        Args:
            model_info: Informations du modèle
        """
        st.subheader("📈 Importance des Variables")
        
        # Importance simulée basée sur l'expérience typique
        feature_importance = {
            'Age': 0.18,
            'Score de Crédit': 0.16,
            'Solde': 0.14,
            'Nombre de Produits': 0.12,
            'Salaire Estimé': 0.10,
            'Satisfaction': 0.08,
            'Ancienneté': 0.07,
            'Membre Actif': 0.06,
            'Carte de Crédit': 0.04,
            'Plainte': 0.03,
            'Points Gagnés': 0.02
        }
        
        # Création du DataFrame
        df_importance = pd.DataFrame([
            {'Variable': var, 'Importance': imp} 
            for var, imp in feature_importance.items()
        ])
        
        # Graphique horizontal
        fig = px.bar(
            df_importance,
            x='Importance',
            y='Variable',
            orientation='h',
            title="Variables les Plus Importantes pour la Prédiction",
            color='Importance',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Explication
        st.info(
            "💡 **Interprétation :** Les variables en haut du graphique "
            "ont le plus d'influence sur la prédiction de churn. "
            "L'âge et le score de crédit sont les facteurs les plus déterminants."
        )
    
    @staticmethod
    def render_prediction_confidence(result: PredictionResult):
        """
        Affiche un indicateur de confiance de la prédiction.
        
        Args:
            result: Résultat de la prédiction
        """
        st.subheader("🎯 Confiance de la Prédiction")
        
        # Calcul de la confiance basé sur la probabilité
        if result.will_churn:
            confidence = result.probability
        else:
            confidence = 1 - result.probability
        
        # Couleur basée sur la confiance
        if confidence >= 0.8:
            color = "success"
            icon = "🟢"
            message = "Très Haute"
        elif confidence >= 0.6:
            color = "info"
            icon = "🔵"
            message = "Haute"
        elif confidence >= 0.4:
            color = "warning"
            icon = "🟡"
            message = "Modérée"
        else:
            color = "error"
            icon = "🔴"
            message = "Faible"
        
        # Affichage
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Confiance", f"{confidence:.1%}")
        
        with col2:
            getattr(st, color)(f"{icon} **{message}**")
        
        with col3:
            # Barre de progression
            st.progress(confidence)
        
        # Recommandation basée sur la confiance
        if confidence < 0.6:
            st.warning(
                "⚠️ **Attention :** Confiance modérée. "
                "Il est recommandé de collecter plus d'informations "
                "sur ce client avant de prendre des décisions importantes."
            )
    
    @staticmethod
    def render_comparison_metrics(customer_data: CustomerData):
        """
        Compare les métriques du client avec les moyennes.
        
        Args:
            customer_data: Données du client
        """
        st.subheader("📊 Comparaison avec la Base Clients")
        
        # Moyennes simulées de la base clients
        averages = {
            'credit_score': 650,
            'age': 40,
            'balance': 75000,
            'estimated_salary': 80000,
            'satisfaction_score': 3.2,
            'tenure': 5.1
        }
        
        # Création des métriques de comparaison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            credit_delta = customer_data.credit_score - averages['credit_score']
            st.metric(
                "Score de Crédit",
                customer_data.credit_score,
                delta=f"{credit_delta:+.0f} vs moyenne"
            )
            
            balance_delta = customer_data.balance - averages['balance']
            st.metric(
                "Solde (€)",
                f"{customer_data.balance:,.0f}",
                delta=f"{balance_delta:+,.0f} vs moyenne"
            )
        
        with col2:
            age_delta = customer_data.age - averages['age']
            st.metric(
                "Âge",
                customer_data.age,
                delta=f"{age_delta:+.0f} vs moyenne"
            )
            
            salary_delta = customer_data.estimated_salary - averages['estimated_salary']
            st.metric(
                "Salaire (€)",
                f"{customer_data.estimated_salary:,.0f}",
                delta=f"{salary_delta:+,.0f} vs moyenne"
            )
        
        with col3:
            satisfaction_delta = customer_data.satisfaction_score - averages['satisfaction_score']
            st.metric(
                "Satisfaction",
                customer_data.satisfaction_score,
                delta=f"{satisfaction_delta:+.1f} vs moyenne"
            )
            
            tenure_delta = customer_data.tenure - averages['tenure']
            st.metric(
                "Ancienneté",
                customer_data.tenure,
                delta=f"{tenure_delta:+.1f} vs moyenne"
            )
    
    @staticmethod
    def render_action_recommendations(result: PredictionResult, customer_data: CustomerData):
        """
        Affiche des recommandations d'actions basées sur le profil.
        
        Args:
            result: Résultat de la prédiction
            customer_data: Données du client
        """
        st.subheader("💡 Recommandations d'Actions")
        
        recommendations = []
        
        if result.will_churn:
            if result.probability > 0.7:
                recommendations.append("🚨 **URGENT**: Contact immédiat du client")
                recommendations.append("📞 Appel personnalisé de l'équipe rétention")
                recommendations.append("🎁 Proposition d'offre spéciale exclusive")
            
            if customer_data.satisfaction_score <= 2:
                recommendations.append("😟 Enquête de satisfaction approfondie")
                recommendations.append("🛠️ Résolution prioritaire des problèmes")
            
            if customer_data.num_of_products == 1:
                recommendations.append("🏦 Proposition de produits complémentaires")
                recommendations.append("💳 Offre carte de crédit avec avantages")
            
            if customer_data.balance < 10000:
                recommendations.append("💰 Conseils en épargne personnalisés")
                recommendations.append("📈 Proposition de placements avantageux")
        
        else:
            recommendations.append("✅ Client fidèle - Maintenir la relation")
            
            if customer_data.satisfaction_score >= 4:
                recommendations.append("⭐ Client ambassadeur potentiel")
                recommendations.append("🗣️ Programme de parrainage")
            
            if customer_data.balance > 100000:
                recommendations.append("👑 Invitation aux services Premium")
                recommendations.append("🏆 Gestionnaire de patrimoine dédié")
        
        # Affichage des recommandations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("Aucune action spécifique recommandée pour ce profil.")
