"""
Utilitaires d'export pour l'application de churn.
"""
import streamlit as st
from datetime import datetime
from typing import Optional
import io
import base64

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from data.schemas import CustomerData, PredictionResult
from config.settings import Settings


class PDFExporter:
    """Classe pour exporter les résultats en PDF."""
    
    def __init__(self):
        """Initialise l'exporteur PDF."""
        if not REPORTLAB_AVAILABLE:
            st.warning(
                "⚠️ **Export PDF non disponible**: La bibliothèque ReportLab n'est pas installée. "
                "Exécutez `pip install reportlab` pour activer cette fonctionnalité."
            )
    
    def generate_report(self, customer_data: CustomerData, result: PredictionResult) -> Optional[bytes]:
        """
        Génère un rapport PDF complet.
        
        Args:
            customer_data: Données du client
            result: Résultat de la prédiction
            
        Returns:
            Bytes du PDF ou None si erreur
        """
        if not REPORTLAB_AVAILABLE:
            return None
        
        try:
            # Buffer pour le PDF
            buffer = io.BytesIO()
            
            # Configuration du document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=HexColor('#1f77b4'),
                alignment=1  # Center
            )
            
            # Contenu du PDF
            story = []
            
            # En-tête
            story.append(Paragraph("Rapport d'Analyse de Churn Client", title_style))
            story.append(Spacer(1, 20))
            
            # Date du rapport
            date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
            story.append(Paragraph(f"<b>Date du rapport :</b> {date_str}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Résultat principal
            self._add_main_result(story, result, styles)
            story.append(Spacer(1, 20))
            
            # Profil client
            self._add_customer_profile(story, customer_data, styles)
            story.append(Spacer(1, 20))
            
            # Détails de l'analyse
            self._add_analysis_details(story, result, customer_data, styles)
            story.append(Spacer(1, 20))
            
            # Recommandations
            self._add_recommendations(story, result, customer_data, styles)
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "<i>Rapport généré automatiquement par le système de prédiction de churn</i>",
                styles['Normal']
            ))
            
            # Construction du PDF
            doc.build(story)
            
            # Récupération des bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")
            return None
    
    def _add_main_result(self, story, result: PredictionResult, styles):
        """Ajoute le résultat principal au PDF."""
        # Titre de section
        story.append(Paragraph("🎯 RÉSULTAT DE LA PRÉDICTION", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Résultat en grand
        if result.will_churn:
            risk_text = f"<font color='red'><b>RISQUE DE DÉPART DÉTECTÉ</b></font>"
            prob_text = f"Probabilité de churn : <b>{result.formatted_probability}</b>"
        else:
            risk_text = f"<font color='green'><b>CLIENT FIDÈLE</b></font>"
            prob_text = f"Probabilité de churn : <b>{result.formatted_probability}</b>"
        
        story.append(Paragraph(risk_text, styles['Normal']))
        story.append(Paragraph(prob_text, styles['Normal']))
        story.append(Paragraph(f"Niveau de risque : <b>{result.risk_level}</b>", styles['Normal']))
    
    def _add_customer_profile(self, story, customer_data: CustomerData, styles):
        """Ajoute le profil client au PDF."""
        story.append(Paragraph("👤 PROFIL CLIENT", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Tableau des informations client
        data = [
            ['Caractéristique', 'Valeur'],
            ['Âge', f"{customer_data.age} ans"],
            ['Sexe', customer_data.gender.value],
            ['Pays', customer_data.country.value],
            ['Catégorie', customer_data.category.value],
            ['Score de crédit', str(customer_data.credit_score)],
            ['Ancienneté', f"{customer_data.tenure} années"],
            ['Solde du compte', f"{customer_data.balance:,.0f} €"],
            ['Salaire estimé', f"{customer_data.estimated_salary:,.0f} €"],
            ['Nombre de produits', str(customer_data.num_of_products)],
            ['Carte de crédit', customer_data.has_credit_card.value],
            ['Membre actif', customer_data.is_active_member.value],
            ['Plainte récente', customer_data.complain.value],
            ['Score satisfaction', f"{customer_data.satisfaction_score}/5"],
            ['Points gagnés', f"{customer_data.point_earned:,}"]
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    def _add_analysis_details(self, story, result: PredictionResult, customer_data: CustomerData, styles):
        """Ajoute les détails de l'analyse."""
        story.append(Paragraph("📊 DÉTAILS DE L'ANALYSE", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Facteurs de risque
        story.append(Paragraph("<b>Facteurs identifiés :</b>", styles['Normal']))
        story.append(Spacer(1, 5))
        
        factors = []
        
        if customer_data.age < 30:
            factors.append("• Âge jeune (moins de 30 ans)")
        
        if customer_data.credit_score < 500:
            factors.append("• Score de crédit faible")
        
        if customer_data.satisfaction_score <= 2:
            factors.append("• Score de satisfaction très bas")
        
        if customer_data.complain.value == "Oui":
            factors.append("• Plainte récente déposée")
        
        if customer_data.num_of_products == 1:
            factors.append("• Un seul produit utilisé")
        
        if customer_data.balance < 10000:
            factors.append("• Solde du compte relativement faible")
        
        if not factors:
            factors.append("• Aucun facteur de risque majeur identifié")
        
        for factor in factors[:5]:  # Limite à 5 facteurs
            story.append(Paragraph(factor, styles['Normal']))
    
    def _add_recommendations(self, story, result: PredictionResult, customer_data: CustomerData, styles):
        """Ajoute les recommandations."""
        story.append(Paragraph("💡 RECOMMANDATIONS", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        recommendations = []
        
        if result.will_churn:
            if result.probability > 0.7:
                recommendations.append("🚨 PRIORITÉ ÉLEVÉE : Contact immédiat du client requis")
                recommendations.append("📞 Appel personnalisé de l'équipe de rétention")
                recommendations.append("🎁 Proposition d'offre spéciale ou de remise")
            
            if customer_data.satisfaction_score <= 2:
                recommendations.append("😟 Enquête de satisfaction approfondie")
                recommendations.append("🛠️ Résolution prioritaire des problèmes identifiés")
            
            if customer_data.num_of_products == 1:
                recommendations.append("🏦 Proposition de produits complémentaires")
                recommendations.append("💳 Offre de carte de crédit avec avantages")
        else:
            recommendations.append("✅ Client fidèle - Maintenir la relation actuelle")
            
            if customer_data.satisfaction_score >= 4:
                recommendations.append("⭐ Client ambassadeur potentiel")
                recommendations.append("🗣️ Inclusion dans le programme de parrainage")
        
        if not recommendations:
            recommendations.append("• Surveillance périodique recommandée")
        
        for i, rec in enumerate(recommendations[:6], 1):  # Limite à 6 recommandations
            story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
    
    @staticmethod
    def create_download_link(pdf_bytes: bytes, filename: str) -> str:
        """
        Crée un lien de téléchargement pour le PDF.
        
        Args:
            pdf_bytes: Contenu du PDF en bytes
            filename: Nom du fichier
            
        Returns:
            HTML du lien de téléchargement
        """
        b64 = base64.b64encode(pdf_bytes).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Télécharger le rapport PDF</a>'


class CSVExporter:
    """Classe pour exporter les données en CSV."""
    
    @staticmethod
    def export_prediction_data(customer_data: CustomerData, result: PredictionResult) -> str:
        """
        Exporte les données de prédiction en format CSV.
        
        Args:
            customer_data: Données du client
            result: Résultat de la prédiction
            
        Returns:
            Contenu CSV sous forme de string
        """
        import pandas as pd
        
        # Création du dictionnaire de données
        data = {
            'Date_Prediction': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Age': [customer_data.age],
            'Sexe': [customer_data.gender.value],
            'Pays': [customer_data.country.value],
            'Categorie': [customer_data.category.value],
            'Score_Credit': [customer_data.credit_score],
            'Anciennete': [customer_data.tenure],
            'Solde': [customer_data.balance],
            'Salaire_Estime': [customer_data.estimated_salary],
            'Nb_Produits': [customer_data.num_of_products],
            'Carte_Credit': [customer_data.has_credit_card.value],
            'Membre_Actif': [customer_data.is_active_member.value],
            'Plainte': [customer_data.complain.value],
            'Score_Satisfaction': [customer_data.satisfaction_score],
            'Points_Gagnes': [customer_data.point_earned],
            'Prediction_Churn': [result.prediction],
            'Probabilite_Churn': [result.probability],
            'Niveau_Risque': [result.risk_level]
        }
        
        # Création du DataFrame et export CSV
        df = pd.DataFrame(data)
        return df.to_csv(index=False, sep=';')
