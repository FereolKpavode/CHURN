"""
Composants d'interface pour l'explainability et le monitoring avancé.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional

from data.schemas import CustomerData, PredictionResult
from models.explainer import SHAPExplainer, ModelMonitor, AlertSystem


class ExplainabilityComponents:
    """Composants pour l'explainability SHAP."""
    
    @staticmethod
    def render_shap_explanation(customer_data: CustomerData, result: PredictionResult):
        """
        Affiche l'explication SHAP détaillée pour un client.
        
        Args:
            customer_data: Données du client
            result: Résultat de la prédiction
        """
        st.subheader("🔍 Explication Détaillée (SHAP)")
        
        # Initialisation de l'explainer
        explainer = SHAPExplainer()
        
        with st.spinner("Calcul des explications SHAP..."):
            shap_dict = explainer.get_shap_explanation(customer_data)
        
        if shap_dict is None:
            st.warning(
                "⚠️ Explications SHAP non disponibles. "
                "Installez les dépendances : `pip install shap matplotlib seaborn`"
            )
            return
        
        # Affichage des résultats
        ExplainabilityComponents._render_shap_summary(shap_dict)
        
        # Onglets pour différentes vues
        tab1, tab2, tab3 = st.tabs(["📊 Impact des Variables", "💬 Interprétation", "⚖️ Comparaison"])
        
        with tab1:
            ExplainabilityComponents._render_shap_waterfall(shap_dict)
            ExplainabilityComponents._render_shap_bar_chart(shap_dict)
        
        with tab2:
            ExplainabilityComponents._render_shap_interpretation(shap_dict)
        
        with tab3:
            ExplainabilityComponents._render_importance_comparison(explainer)
    
    @staticmethod
    def _render_shap_summary(shap_dict: Dict):
        """Affiche le résumé SHAP."""
        base_value = shap_dict['base_value']
        prediction = shap_dict['prediction']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Prédiction de Base",
                f"{base_value:.3f}",
                help="Probabilité moyenne de churn dans la population"
            )
        
        with col2:
            st.metric(
                "Prédiction Finale",
                f"{prediction:.3f}",
                delta=f"{prediction - base_value:+.3f}"
            )
        
        with col3:
            impact = "Positif" if prediction > base_value else "Négatif"
            color = "🔴" if prediction > base_value else "🟢"
            st.metric(
                "Impact Global",
                f"{color} {impact}",
                help="L'impact global des caractéristiques du client"
            )
    
    @staticmethod
    def _render_shap_waterfall(shap_dict: Dict):
        """Affiche le graphique waterfall SHAP."""
        st.subheader("🌊 Analyse Waterfall")
        
        shap_values = shap_dict['shap_values']
        base_value = shap_dict['base_value']
        
        # Préparation des données pour le waterfall
        sorted_features = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]  # Top 10 features
        
        features = ['Base'] + [f[0] for f in sorted_features] + ['Final']
        values = [base_value] + [f[1] for f in sorted_features] + [0]
        cumulative = [base_value]
        
        for val in values[1:-1]:
            cumulative.append(cumulative[-1] + val)
        cumulative.append(cumulative[-1])
        
        # Création du graphique waterfall
        fig = go.Figure()
        
        # Barre de base
        fig.add_trace(go.Bar(
            name='Base',
            x=[features[0]],
            y=[values[0]],
            marker_color='lightblue'
        ))
        
        # Barres d'impact
        for i, (feature, shap_val) in enumerate(sorted_features, 1):
            color = 'salmon' if shap_val > 0 else 'lightgreen'
            fig.add_trace(go.Bar(
                name=feature,
                x=[feature],
                y=[abs(shap_val)],
                base=[cumulative[i-1] if shap_val > 0 else cumulative[i-1] - abs(shap_val)],
                marker_color=color
            ))
        
        # Barre finale
        fig.add_trace(go.Bar(
            name='Final',
            x=[features[-1]],
            y=[cumulative[-2]],
            marker_color='navy'
        ))
        
        fig.update_layout(
            title="Impact Cumulé des Variables (Waterfall SHAP)",
            xaxis_title="Variables",
            yaxis_title="Probabilité de Churn",
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_shap_bar_chart(shap_dict: Dict):
        """Affiche le graphique en barres des SHAP values."""
        st.subheader("📊 Impact par Variable")
        
        shap_values = shap_dict['shap_values']
        feature_values = shap_dict['feature_values']
        
        # Tri par impact absolu
        sorted_items = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:12]  # Top 12 features
        
        features = [item[0] for item in sorted_items]
        impacts = [item[1] for item in sorted_items]
        values = [feature_values[f] for f in features]
        
        # Couleurs selon l'impact
        colors = ['red' if x > 0 else 'green' for x in impacts]
        
        # Création du graphique
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=impacts,
            y=features,
            orientation='h',
            marker_color=colors,
            text=[f"Valeur: {v}" for v in values],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Impact SHAP par Variable",
            xaxis_title="Impact sur la Probabilité de Churn",
            yaxis_title="Variables",
            height=600
        )
        
        # Ligne verticale à zéro
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_shap_interpretation(shap_dict: Dict):
        """Affiche l'interprétation en langage naturel."""
        st.subheader("💬 Interprétation en Langage Naturel")
        
        interpretations = SHAPExplainer.interpret_shap_values(shap_dict)
        
        if interpretations:
            st.write("**Facteurs les plus influents :**")
            
            for i, (feature, interpretation) in enumerate(interpretations.items(), 1):
                impact_icon = "🔴" if shap_dict['shap_values'][feature] > 0 else "🟢"
                st.write(f"{i}. {impact_icon} {interpretation}")
        
        # Recommandations basées sur SHAP
        st.markdown("---")
        st.write("**💡 Recommandations basées sur l'analyse :**")
        
        shap_values = shap_dict['shap_values']
        feature_values = shap_dict['feature_values']
        
        recommendations = []
        
        # Analyse des facteurs négatifs (qui réduisent le churn)
        negative_factors = {k: v for k, v in shap_values.items() if v < -0.05}
        positive_factors = {k: v for k, v in shap_values.items() if v > 0.05}
        
        if 'satisfaction score' in positive_factors:
            recommendations.append("📞 Enquête de satisfaction urgente recommandée")
        
        if 'age' in positive_factors and feature_values['age'] < 30:
            recommendations.append("🎯 Proposer des produits adaptés aux jeunes professionnels")
        
        if 'numofproducts' in positive_factors and feature_values['numofproducts'] == 1:
            recommendations.append("🏦 Stratégie de cross-selling pour diversifier le portefeuille")
        
        if 'balance' in positive_factors and feature_values['balance'] < 10000:
            recommendations.append("💰 Accompagnement en épargne et gestion financière")
        
        if not recommendations:
            recommendations.append("✅ Profil relativement stable, maintenir la relation actuelle")
        
        for rec in recommendations:
            st.write(f"• {rec}")
    
    @staticmethod
    def _render_importance_comparison(explainer: SHAPExplainer):
        """Compare l'importance SHAP vs importance du modèle."""
        st.subheader("⚖️ SHAP vs Importance du Modèle")
        
        comparison = explainer.get_feature_importance_comparison()
        
        if comparison is None:
            st.warning("Comparaison non disponible")
            return
        
        # Préparation des données
        features = list(comparison['model_importance'].keys())[:10]  # Top 10
        model_imp = [comparison['model_importance'][f] for f in features]
        shap_imp = [comparison['shap_importance'][f] for f in features]
        
        # Normalisation pour comparaison
        model_imp_norm = [x / max(model_imp) for x in model_imp]
        shap_imp_norm = [x / max(shap_imp) for x in shap_imp]
        
        # Graphique de comparaison
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Importance Modèle',
            x=features,
            y=model_imp_norm,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Importance SHAP',
            x=features,
            y=shap_imp_norm,
            marker_color='orange'
        ))
        
        fig.update_layout(
            title="Comparaison des Importances (Normalisées)",
            xaxis_title="Variables",
            yaxis_title="Importance Relative",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "💡 **Interprétation** : L'importance du modèle montre l'impact global d'une variable, "
            "tandis que SHAP montre l'impact spécifique sur cet échantillon."
        )


class MonitoringComponents:
    """Composants pour le monitoring avancé."""
    
    @staticmethod
    def render_monitoring_dashboard():
        """Affiche le dashboard de monitoring complet."""
        st.header("📊 Monitoring Avancé du Modèle")
        
        # Récupération des données
        monitor = ModelMonitor()
        performance_data = monitor.simulate_model_performance()
        drift_data = monitor.detect_data_drift()
        trends_data = monitor.get_prediction_trends()
        
        # Alertes système
        MonitoringComponents._render_alerts_section(performance_data, drift_data)
        
        # Métriques de performance
        MonitoringComponents._render_performance_metrics(performance_data)
        
        # Détection de dérive
        MonitoringComponents._render_drift_detection(drift_data)
        
        # Tendances et prédictions
        MonitoringComponents._render_prediction_trends(trends_data)
        
        # Alertes clients
        MonitoringComponents._render_client_alerts()
    
    @staticmethod
    def _render_alerts_section(performance_data: Dict, drift_data: Dict):
        """Affiche la section des alertes."""
        st.subheader("🚨 Alertes Système")
        
        alert_system = AlertSystem()
        alerts = alert_system.check_alerts(performance_data, drift_data)
        
        if not alerts:
            st.success("✅ Aucune alerte active - Système en fonctionnement normal")
            return
        
        # Groupement des alertes par niveau
        critical_alerts = [a for a in alerts if a['level'] == 'CRITICAL']
        warning_alerts = [a for a in alerts if a['level'] == 'WARNING']
        
        if critical_alerts:
            st.error(f"🔴 **{len(critical_alerts)} alerte(s) critique(s)**")
            for alert in critical_alerts:
                with st.expander(f"🚨 {alert['type']} - {alert['message']}", expanded=True):
                    st.write(f"**Action recommandée :** {alert['action']}")
                    st.write(f"**Timestamp :** {alert['timestamp']}")
        
        if warning_alerts:
            st.warning(f"🟡 **{len(warning_alerts)} alerte(s) d'attention**")
            for alert in warning_alerts:
                with st.expander(f"⚠️ {alert['type']} - {alert['message']}"):
                    st.write(f"**Action recommandée :** {alert['action']}")
                    st.write(f"**Timestamp :** {alert['timestamp']}")
    
    @staticmethod
    def _render_performance_metrics(performance_data: Dict):
        """Affiche les métriques de performance."""
        st.subheader("📈 Performance du Modèle")
        
        # Métriques actuelles
        col1, col2, col3, col4 = st.columns(4)
        
        current_accuracy = performance_data['accuracy'][-1]
        current_precision = performance_data['precision'][-1]
        current_recall = performance_data['recall'][-1]
        current_f1 = performance_data['f1_score'][-1]
        
        with col1:
            delta_acc = current_accuracy - performance_data['accuracy'][-7]
            st.metric("Précision", f"{current_accuracy:.1%}", delta=f"{delta_acc:+.1%}")
        
        with col2:
            delta_prec = current_precision - performance_data['precision'][-7]
            st.metric("Precision", f"{current_precision:.1%}", delta=f"{delta_prec:+.1%}")
        
        with col3:
            delta_rec = current_recall - performance_data['recall'][-7]
            st.metric("Recall", f"{current_recall:.1%}", delta=f"{delta_rec:+.1%}")
        
        with col4:
            delta_f1 = current_f1 - performance_data['f1_score'][-7]
            st.metric("F1-Score", f"{current_f1:.1%}", delta=f"{delta_f1:+.1%}")
        
        # Graphique d'évolution
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Précision', 'Precision', 'Recall', 'F1-Score'),
            vertical_spacing=0.12
        )
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        positions = [(1,1), (1,2), (2,1), (2,2)]
        
        for metric, (row, col) in zip(metrics, positions):
            fig.add_trace(
                go.Scatter(
                    x=performance_data['dates'],
                    y=performance_data[metric],
                    mode='lines+markers',
                    name=metric.capitalize(),
                    line=dict(width=2)
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title="Évolution des Métriques (30 derniers jours)",
            height=600,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_drift_detection(drift_data: Dict):
        """Affiche la détection de dérive des données."""
        st.subheader("🌊 Détection de Dérive des Données")
        
        # Tableau de statut
        drift_df = pd.DataFrame([
            {
                'Variable': feature,
                'Score de Dérive': f"{info['drift_score']:.3f}",
                'Seuil': f"{info['threshold']:.3f}",
                'Statut': info['status']
            }
            for feature, info in drift_data.items()
        ])
        
        # Coloration du statut
        def color_status(val):
            if val == 'CRITICAL':
                return 'background-color: #ffebee'
            elif val == 'ALERT':
                return 'background-color: #fff3e0'
            elif val == 'OK':
                return 'background-color: #e8f5e8'
            return ''
        
        st.dataframe(
            drift_df.style.applymap(color_status, subset=['Statut']),
            use_container_width=True
        )
        
        # Graphique de dérive
        features = list(drift_data.keys())
        drift_scores = [drift_data[f]['drift_score'] for f in features]
        threshold = drift_data[features[0]]['threshold']
        
        fig = go.Figure()
        
        # Barres de dérive
        colors = [
            'red' if drift_data[f]['status'] == 'CRITICAL' 
            else 'orange' if drift_data[f]['status'] == 'ALERT' 
            else 'green' 
            for f in features
        ]
        
        fig.add_trace(go.Bar(
            x=features,
            y=drift_scores,
            marker_color=colors,
            name='Score de Dérive'
        ))
        
        # Ligne de seuil
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Seuil: {threshold}"
        )
        
        fig.update_layout(
            title="Scores de Dérive par Variable",
            xaxis_title="Variables",
            yaxis_title="Score de Dérive",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_prediction_trends(trends_data: Dict):
        """Affiche les tendances de prédiction."""
        st.subheader("📊 Tendances de Prédiction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volume de prédictions
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=trends_data['dates'],
                y=trends_data['daily_predictions'],
                mode='lines+markers',
                name='Prédictions/jour',
                line=dict(color='blue', width=2)
            ))
            
            fig1.update_layout(
                title="Volume de Prédictions Quotidiennes",
                xaxis_title="Date",
                yaxis_title="Nombre de Prédictions",
                height=400
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Taux de churn quotidien
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=trends_data['dates'],
                y=[rate * 100 for rate in trends_data['daily_churn_rate']],
                mode='lines+markers',
                name='Taux de churn (%)',
                line=dict(color='red', width=2),
                fill='tonexty'
            ))
            
            fig2.update_layout(
                title="Évolution du Taux de Churn",
                xaxis_title="Date",
                yaxis_title="Taux de Churn (%)",
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Clients à haut risque
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=trends_data['dates'],
            y=trends_data['high_risk_clients'],
            name='Clients Haut Risque',
            marker_color='orange'
        ))
        
        fig3.update_layout(
            title="Clients à Haut Risque Identifiés par Jour",
            xaxis_title="Date",
            yaxis_title="Nombre de Clients",
            height=400
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    @staticmethod
    def _render_client_alerts():
        """Affiche les alertes clients à haut risque."""
        st.subheader("🚨 Clients Nécessitant une Action Immédiate")
        
        alert_system = AlertSystem()
        high_risk_clients = alert_system.get_client_risk_alerts()
        
        for client in high_risk_clients:
            with st.expander(
                f"🔴 {client['client_id']} - Probabilité: {client['churn_probability']:.1%}",
                expanded=True
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Facteurs de risque :**")
                    for factor in client['risk_factors']:
                        st.write(f"• {factor}")
                    
                    st.write(f"**Dernière prédiction :** {client['last_prediction']}")
                
                with col2:
                    st.write("**Action recommandée :**")
                    st.warning(client['recommended_action'])
                    
                    if st.button(f"Marquer comme traité", key=f"btn_{client['client_id']}"):
                        st.success("✅ Client marqué comme traité")
        
        if not high_risk_clients:
            st.success("✅ Aucun client en situation critique actuellement")
