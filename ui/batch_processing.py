"""
Composants pour le traitement par lots des prédictions.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import io
from datetime import datetime

from data.schemas import CustomerData, PredictionResult
from data.validator import DataValidator
from models.predictor import ChurnPredictor
from config.constants import Gender, Country, Category, BinaryChoice
from utils.exceptions import ChurnPredictionError, DataValidationError
from utils.export import CSVExporter


class BatchProcessor:
    """Classe pour le traitement par lots des prédictions."""
    
    def __init__(self):
        """Initialise le processeur par lots."""
        self.predictor = ChurnPredictor()
    
    @staticmethod
    def render_batch_page():
        """Affiche la page de traitement par lots."""
        st.header("📊 Prédictions par Lots")
        
        st.info(
            "💡 **Mode d'emploi :** Téléchargez le modèle CSV, remplissez-le avec vos données "
            "client, puis uploadez-le pour obtenir des prédictions en masse."
        )
        
        # Section 1: Template CSV
        BatchProcessor._render_template_section()
        
        st.markdown("---")
        
        # Section 2: Upload et traitement
        BatchProcessor._render_upload_section()
    
    @staticmethod
    def _render_template_section():
        """Affiche la section de téléchargement du template."""
        st.subheader("📋 1. Télécharger le Modèle CSV")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(
                "Téléchargez d'abord le modèle CSV avec les colonnes requises "
                "et des exemples de données."
            )
        
        with col2:
            if st.button("📥 Télécharger Modèle CSV", use_container_width=True):
                template_csv = BatchProcessor._generate_template_csv()
                st.download_button(
                    label="💾 Modèle CSV",
                    data=template_csv,
                    file_name="modele_prediction_churn.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Affichage du format attendu
        with st.expander("📖 Format des Données Attendu"):
            st.write("**Colonnes requises :**")
            columns_info = {
                "age": "Âge du client (18-100)",
                "gender": "Sexe (Homme/Femme)",
                "country": "Pays (France/Allemagne/Espagne)",
                "category": "Catégorie (RUBIS/SILVER/GOLD/PLATINUM)",
                "credit_score": "Score de crédit (300-900)",
                "tenure": "Ancienneté en années (0-20)",
                "balance": "Solde du compte (0-300000)",
                "estimated_salary": "Salaire estimé (0-300000)",
                "num_of_products": "Nombre de produits (1-4)",
                "has_credit_card": "Carte de crédit (Oui/Non)",
                "is_active_member": "Membre actif (Oui/Non)",
                "complain": "Plainte récente (Oui/Non)",
                "satisfaction_score": "Score satisfaction (0-5)",
                "point_earned": "Points gagnés (0-100000)"
            }
            
            for col, desc in columns_info.items():
                st.write(f"• **{col}** : {desc}")
    
    @staticmethod
    def _render_upload_section():
        """Affiche la section d'upload et de traitement."""
        st.subheader("📤 2. Upload et Traitement")
        
        uploaded_file = st.file_uploader(
            "Choisir un fichier CSV",
            type=['csv'],
            help="Uploadez votre fichier CSV avec les données clients"
        )
        
        if uploaded_file is not None:
            try:
                # Lecture du fichier
                df = pd.read_csv(uploaded_file, sep=';')
                
                st.success(f"✅ Fichier chargé avec succès : {len(df)} lignes détectées")
                
                # Aperçu des données
                with st.expander("👀 Aperçu des Données"):
                    st.dataframe(df.head(10), use_container_width=True)
                
                # Validation et traitement
                if st.button("🎯 Lancer les Prédictions", type="primary", use_container_width=True):
                    BatchProcessor._process_batch_predictions(df)
            
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
                st.write("💡 Vérifiez que votre fichier CSV utilise le bon format et encodage.")
    
    @staticmethod
    def _generate_template_csv() -> str:
        """Génère un template CSV avec des exemples."""
        template_data = {
            'age': [35, 42, 28, 56, 31],
            'gender': ['Homme', 'Femme', 'Homme', 'Femme', 'Homme'],
            'country': ['France', 'Allemagne', 'Espagne', 'France', 'Allemagne'],
            'category': ['SILVER', 'GOLD', 'RUBIS', 'PLATINUM', 'SILVER'],
            'credit_score': [650, 720, 580, 800, 690],
            'tenure': [5, 8, 2, 12, 6],
            'balance': [75000, 120000, 25000, 180000, 95000],
            'estimated_salary': [65000, 85000, 45000, 120000, 70000],
            'num_of_products': [2, 3, 1, 4, 2],
            'has_credit_card': ['Oui', 'Oui', 'Non', 'Oui', 'Oui'],
            'is_active_member': ['Oui', 'Oui', 'Non', 'Oui', 'Non'],
            'complain': ['Non', 'Non', 'Oui', 'Non', 'Non'],
            'satisfaction_score': [4, 5, 2, 4, 3],
            'point_earned': [1500, 2800, 200, 5000, 1200]
        }
        
        df_template = pd.DataFrame(template_data)
        return df_template.to_csv(index=False, sep=';')
    
    @staticmethod
    def _process_batch_predictions(df: pd.DataFrame):
        """Traite les prédictions par lots."""
        processor = BatchProcessor()
        
        with st.spinner("Traitement des prédictions en cours..."):
            results = []
            errors = []
            
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            for idx, row in df.iterrows():
                try:
                    # Conversion en CustomerData
                    customer_data = processor._row_to_customer_data(row)
                    
                    # Validation
                    validation_errors = DataValidator.validate_customer_data(customer_data.__dict__)
                    if validation_errors:
                        errors.append(f"Ligne {idx + 1}: {'; '.join(validation_errors)}")
                        continue
                    
                    # Prédiction
                    result = processor.predictor.predict(customer_data)
                    
                    # Stockage du résultat
                    result_data = {
                        'Ligne': idx + 1,
                        'Age': customer_data.age,
                        'Pays': customer_data.country.value,
                        'Categorie': customer_data.category.value,
                        'Score_Credit': customer_data.credit_score,
                        'Prediction_Churn': result.prediction,
                        'Probabilite_Churn': result.probability,
                        'Niveau_Risque': result.risk_level,
                        'Decision': 'PARTIR' if result.will_churn else 'RESTER'
                    }
                    results.append(result_data)
                
                except Exception as e:
                    errors.append(f"Ligne {idx + 1}: Erreur de traitement - {str(e)}")
                
                # Mise à jour de la barre de progression
                progress_bar.progress((idx + 1) / total_rows)
            
            # Affichage des résultats
            processor._display_batch_results(results, errors, df)
    
    def _row_to_customer_data(self, row: pd.Series) -> CustomerData:
        """Convertit une ligne de DataFrame en objet CustomerData."""
        try:
            return CustomerData(
                credit_score=int(row['credit_score']),
                age=int(row['age']),
                tenure=int(row['tenure']),
                balance=float(row['balance']),
                num_of_products=int(row['num_of_products']),
                estimated_salary=float(row['estimated_salary']),
                satisfaction_score=int(row['satisfaction_score']),
                point_earned=int(row['point_earned']),
                has_credit_card=BinaryChoice.YES if row['has_credit_card'] == 'Oui' else BinaryChoice.NO,
                is_active_member=BinaryChoice.YES if row['is_active_member'] == 'Oui' else BinaryChoice.NO,
                complain=BinaryChoice.YES if row['complain'] == 'Oui' else BinaryChoice.NO,
                gender=Gender.MALE if row['gender'] == 'Homme' else Gender.FEMALE,
                country=Country.FRANCE if row['country'] == 'France' 
                        else Country.GERMANY if row['country'] == 'Allemagne' 
                        else Country.SPAIN,
                category=Category.RUBIS if row['category'] == 'RUBIS'
                         else Category.SILVER if row['category'] == 'SILVER'
                         else Category.GOLD if row['category'] == 'GOLD'
                         else Category.PLATINUM
            )
        except (ValueError, KeyError) as e:
            raise DataValidationError(f"Erreur de conversion des données : {e}")
    
    @staticmethod
    def _display_batch_results(results: List[Dict], errors: List[str], original_df: pd.DataFrame):
        """Affiche les résultats du traitement par lots."""
        st.markdown("---")
        st.subheader("📊 Résultats du Traitement")
        
        # Métriques de synthèse
        total_processed = len(results)
        total_errors = len(errors)
        churn_predictions = sum(1 for r in results if r['Prediction_Churn'] == 1)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Traité", total_processed)
        
        with col2:
            st.metric("Erreurs", total_errors)
        
        with col3:
            st.metric("Prédictions Churn", churn_predictions)
        
        with col4:
            if total_processed > 0:
                churn_rate = (churn_predictions / total_processed) * 100
                st.metric("Taux de Churn", f"{churn_rate:.1f}%")
        
        # Erreurs
        if errors:
            with st.expander(f"❌ Erreurs de Traitement ({len(errors)})"):
                for error in errors:
                    st.error(error)
        
        # Résultats détaillés
        if results:
            st.subheader("📋 Résultats Détaillés")
            
            df_results = pd.DataFrame(results)
            
            # Coloration selon le risque
            def color_risk(val):
                if val == 'PARTIR':
                    return 'background-color: #ffebee'
                elif val == 'RESTER':
                    return 'background-color: #e8f5e8'
                return ''
            
            st.dataframe(
                df_results.style.applymap(color_risk, subset=['Decision']),
                use_container_width=True
            )
            
            # Export des résultats
            st.subheader("📥 Export des Résultats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV des résultats
                csv_results = df_results.to_csv(index=False, sep=';')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                st.download_button(
                    label="📊 Télécharger Résultats CSV",
                    data=csv_results,
                    file_name=f"resultats_batch_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Analyse par segments
                if st.button("📈 Générer Analyse Segments", use_container_width=True):
                    BatchProcessor._generate_segment_analysis(df_results)
    
    @staticmethod
    def _generate_segment_analysis(df_results: pd.DataFrame):
        """Génère une analyse par segments."""
        st.subheader("🎯 Analyse par Segments")
        
        # Analyse par pays
        st.write("**Analyse par Pays:**")
        country_analysis = df_results.groupby('Pays').agg({
            'Prediction_Churn': ['count', 'sum'],
            'Probabilite_Churn': 'mean'
        }).round(3)
        
        country_analysis.columns = ['Total_Clients', 'Churn_Count', 'Prob_Moyenne']
        country_analysis['Taux_Churn_%'] = (country_analysis['Churn_Count'] / country_analysis['Total_Clients'] * 100).round(1)
        
        st.dataframe(country_analysis, use_container_width=True)
        
        # Analyse par catégorie
        st.write("**Analyse par Catégorie:**")
        category_analysis = df_results.groupby('Categorie').agg({
            'Prediction_Churn': ['count', 'sum'],
            'Probabilite_Churn': 'mean'
        }).round(3)
        
        category_analysis.columns = ['Total_Clients', 'Churn_Count', 'Prob_Moyenne']
        category_analysis['Taux_Churn_%'] = (category_analysis['Churn_Count'] / category_analysis['Total_Clients'] * 100).round(1)
        
        st.dataframe(category_analysis, use_container_width=True)
        
        # Graphique de distribution
        import plotly.express as px
        
        fig = px.histogram(
            df_results, 
            x='Niveau_Risque',
            color='Decision',
            title="Distribution des Niveaux de Risque",
            color_discrete_map={'PARTIR': '#ff6b6b', 'RESTER': '#51cf66'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
