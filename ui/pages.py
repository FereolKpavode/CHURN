"""
Pages de l'application Streamlit.
"""
import streamlit as st
from typing import Dict, Any

from data.schemas import CustomerData, PredictionResult
from models.predictor import ChurnPredictor
from ui.components import InputComponents, DisplayComponents
from ui.visualizations import VisualizationComponents
from ui.explainability import ExplainabilityComponents, MonitoringComponents
from data.validator import DataValidator
from utils.exceptions import ChurnPredictionError


class PredictionPage:
    """Page principale de prédiction."""
    
    @staticmethod
    def render():
        """Affiche la page de prédiction."""
        st.header("🎯 Prédiction de Churn Individual")
        
        try:
            # Initialisation du prédicteur
            predictor = ChurnPredictor()
            
            # Collecte des données utilisateur
            user_data = PredictionPage._collect_user_inputs()
            
            # Bouton de prédiction
            if st.button("🎯 Prédire le Churn", type="primary", use_container_width=True):
                with st.spinner("Analyse en cours..."):
                    
                    # Validation des données
                    validation_errors = DataValidator.validate_customer_data(user_data)
                    business_errors = DataValidator.validate_business_rules(user_data)
                    all_errors = validation_errors + business_errors
                    
                    if DisplayComponents.render_error_message(all_errors):
                        st.stop()
                    
                    # Création de l'objet CustomerData
                    customer_data = CustomerData(**user_data)
                    
                    # Prédiction
                    result = predictor.predict(customer_data)
                    
                    # Affichage des résultats avec analytics
                    PredictionPage._render_detailed_results(result, customer_data, predictor)
        
        except ChurnPredictionError as e:
            st.error(f"❌ Erreur de prédiction : {e}")
        except Exception as e:
            st.error("❌ Une erreur inattendue s'est produite. Veuillez contacter l'administrateur.")
    
    @staticmethod
    def _collect_user_inputs() -> Dict[str, Any]:
        """Collecte les données saisies par l'utilisateur."""
        # Organisation en colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Informations Personnelles")
            
            age = InputComponents.render_numeric_input(
                "Âge", "age", 
                "Âge du client en années"
            )
            
            from config.constants import Gender, Country, Category, BinaryChoice
            
            gender = InputComponents.render_selectbox(
                "Sexe", Gender,
                "Sexe du client"
            )
            
            country = InputComponents.render_selectbox(
                "Pays", Country,
                "Pays de résidence du client"
            )
            
            category = InputComponents.render_selectbox(
                "Catégorie", Category,
                "Catégorie de compte du client"
            )
            
            st.subheader("🏦 Informations Bancaires")
            
            credit_score = InputComponents.render_numeric_input(
                "Score de Crédit", "credit_score",
                "Score de crédit du client (300-900)"
            )
            
            tenure = InputComponents.render_slider_input(
                "Ancienneté (années)", "tenure",
                "Nombre d'années depuis l'ouverture du compte"
            )
        
        with col2:
            st.subheader("💰 Informations Financières")
            
            balance = InputComponents.render_numeric_input(
                "Solde du Compte (€)", "balance",
                "Solde actuel du compte principal"
            )
            
            estimated_salary = InputComponents.render_numeric_input(
                "Salaire Estimé (€)", "estimated_salary",
                "Salaire annuel estimé du client"
            )
            
            num_of_products = InputComponents.render_slider_input(
                "Nombre de Produits", "num_of_products",
                "Nombre de produits bancaires utilisés"
            )
            
            point_earned = InputComponents.render_numeric_input(
                "Points Gagnés", "point_earned",
                "Points de fidélité accumulés"
            )
            
            st.subheader("🔍 Comportement Client")
            
            has_credit_card = InputComponents.render_selectbox(
                "Possède une Carte de Crédit", BinaryChoice,
                "Le client possède-t-il une carte de crédit ?"
            )
            
            is_active_member = InputComponents.render_selectbox(
                "Membre Actif", BinaryChoice,
                "Le client est-il un membre actif ?"
            )
            
            complain = InputComponents.render_selectbox(
                "A Déposé une Plainte", BinaryChoice,
                "Le client a-t-il déposé une plainte récemment ?"
            )
            
            satisfaction_score = InputComponents.render_slider_input(
                "Score de Satisfaction", "satisfaction_score",
                "Score de satisfaction client (0-5)"
            )
        
        return {
            'credit_score': int(credit_score),
            'age': int(age),
            'tenure': int(tenure),
            'balance': float(balance),
            'num_of_products': int(num_of_products),
            'estimated_salary': float(estimated_salary),
            'satisfaction_score': int(satisfaction_score),
            'point_earned': int(point_earned),
            'has_credit_card': has_credit_card,
            'is_active_member': is_active_member,
            'complain': complain,
            'gender': gender,
            'country': country,
            'category': category
        }
    
    @staticmethod
    def _render_detailed_results(result: PredictionResult, customer_data: CustomerData, predictor: ChurnPredictor):
        """Affiche les résultats détaillés avec analytics."""
        
        # Résultat principal
        DisplayComponents.render_prediction_result(result, customer_data)
        
        # Onglets pour les analyses détaillées
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analytics", "🎯 Profil", "📈 Comparaison", "🔍 SHAP", "💡 Actions"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                VisualizationComponents.render_prediction_confidence(result)
            with col2:
                VisualizationComponents.render_feature_importance(predictor.get_model_info())
        
        with tab2:
            VisualizationComponents.render_customer_profile_radar(customer_data)
            DisplayComponents.render_customer_summary(customer_data)
        
        with tab3:
            VisualizationComponents.render_comparison_metrics(customer_data)
            VisualizationComponents.render_risk_distribution()
        
        with tab4:
            ExplainabilityComponents.render_shap_explanation(customer_data, result)
        
        with tab5:
            VisualizationComponents.render_action_recommendations(result, customer_data)


class AnalyticsPage:
    """Page d'analytics globaux."""
    
    @staticmethod
    def render():
        """Affiche la page d'analytics."""
        st.header("📈 Analytics & Monitoring Avancé")
        
        # Navigation des analytics
        analytics_tab1, analytics_tab2 = st.tabs(["📊 Analytics Globaux", "🔍 Monitoring Modèle"])
        
        with analytics_tab1:
            AnalyticsPage._render_global_analytics()
        
        with analytics_tab2:
            MonitoringComponents.render_monitoring_dashboard()
    
    @staticmethod
    def _render_global_analytics():
        """Affiche les analytics globaux."""
        # Métriques générales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clients", "10,000", delta="150 ce mois")
        
        with col2:
            st.metric("Taux de Churn", "12.5%", delta="-2.1% vs mois dernier")
        
        with col3:
            st.metric("Clients à Risque", "1,250", delta="75 nouveaux")
        
        with col4:
            st.metric("Rétention Réussie", "85%", delta="3% d'amélioration")
        
        st.markdown("---")
        
        # Visualisations globales
        col1, col2 = st.columns(2)
        
        with col1:
            VisualizationComponents.render_risk_distribution()
        
        with col2:
            VisualizationComponents.render_feature_importance({"type": "RandomForestClassifier"})
        
        # Tendances temporelles (simulées)
        st.subheader("📈 Évolution du Taux de Churn")
        
        import pandas as pd
        import plotly.express as px
        
        # Données simulées
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
        churn_rates = [15.2, 14.8, 13.5, 12.9, 12.1, 12.5]
        
        df_trend = pd.DataFrame({
            'Mois': months,
            'Taux de Churn (%)': churn_rates
        })
        
        fig = px.line(df_trend, x='Mois', y='Taux de Churn (%)', 
                     title="Évolution du Taux de Churn (6 derniers mois)")
        fig.update_traces(line_color='#ff6b6b', line_width=3)
        fig.add_hline(y=12.5, line_dash="dash", line_color="gray", 
                     annotation_text="Objectif: 12%")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Segments à risque
        st.subheader("🎯 Segments à Surveiller")
        
        segments_data = {
            'Segment': ['Jeunes 18-25', 'Score crédit < 400', 'Solde < 1000€', 'Satisfaction ≤ 2'],
            'Nombre': [450, 320, 280, 180],
            'Taux Churn': ['18%', '25%', '22%', '45%'],
            'Priorité': ['Moyenne', 'Élevée', 'Élevée', 'Critique']
        }
        
        df_segments = pd.DataFrame(segments_data)
        
        # Coloration basée sur la priorité
        def color_priority(val):
            if val == 'Critique':
                return 'background-color: #ffebee'
            elif val == 'Élevée':
                return 'background-color: #fff3e0'
            elif val == 'Moyenne':
                return 'background-color: #f3e5f5'
            return ''
        
        st.dataframe(
            df_segments.style.applymap(color_priority, subset=['Priorité']),
            use_container_width=True
        )
