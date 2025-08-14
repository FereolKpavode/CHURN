# 📊 Application de Prédiction de Churn Client

Cette application Streamlit permet de prédire si un client bancaire est susceptible de quitter la banque (churn) en utilisant un modèle de machine learning Random Forest.

## 🚀 Fonctionnalités

### 🎯 **Prédiction Individuelle**
- **Interface intuitive** avec validation des données en temps réel
- **Prédiction de churn** avec probabilité et niveau de risque
- **Dashboard analytics** avec graphiques interactifs
- **Profil client radar** et comparaisons
- **Recommandations d'actions** personnalisées

### 📊 **Traitement par Lots**
- **Upload CSV** pour prédictions multiples
- **Template téléchargeable** avec exemples
- **Validation automatique** des données
- **Analyse par segments** (pays, catégorie)
- **Export des résultats** en CSV

### 📥 **Export et Rapports**
- **Génération PDF** de rapports complets
- **Export CSV** des données et prédictions
- **Graphiques et visualisations** intégrés
- **Métriques de performance** du modèle

### 🛡️ **Robustesse**
- **Gestion d'erreurs complète** avec logging
- **Validation multi-niveaux** des données
- **Architecture modulaire** respectant les principes du clean code
- **Interface responsive** et moderne

## 📁 Structure du Projet

```
CHURN/
├── app.py                 # Point d'entrée de l'application
├── config/                # Configuration centralisée
│   ├── constants.py       # Constantes et énumérations
│   └── settings.py        # Paramètres de l'application
├── data/                  # Gestion des données
│   ├── schemas.py         # Schémas de données
│   └── validator.py       # Validation des données
├── models/                # Modèles de machine learning
│   ├── predictor.py       # Classe de prédiction
│   └── random_forest_model.pkl
├── ui/                    # Interface utilisateur
│   └── components.py      # Composants Streamlit réutilisables
├── utils/                 # Utilitaires
│   └── exceptions.py      # Exceptions personnalisées
├── requirements.txt       # Dépendances Python
└── README.md             # Cette documentation
```

## 🛠️ Installation et Lancement

### Prérequis
- Python 3.8+
- pip

### Installation
```bash
# Cloner le repository
git clone <url-du-repo>
cd CHURN

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement
```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

## 📋 Utilisation

### 🎯 **Mode Prédiction Individuelle**
1. **Remplir le formulaire** avec les informations du client
2. **Cliquer sur "Prédire le Churn"** pour lancer l'analyse
3. **Consulter les résultats** dans les onglets Analytics, Profil, Comparaison
4. **Télécharger les rapports** PDF ou CSV
5. **Examiner les recommandations** d'actions à entreprendre

### 📊 **Mode Traitement par Lots**
1. **Télécharger le modèle CSV** depuis l'application
2. **Remplir le fichier** avec vos données clients
3. **Uploader le fichier** dans l'interface
4. **Lancer les prédictions** en masse
5. **Analyser les résultats** par segments
6. **Exporter les résultats** pour utilisation externe

### 📈 **Mode Analytics**
1. **Consulter les métriques** globales de la base clients
2. **Analyser les tendances** de churn
3. **Identifier les segments** à risque
4. **Suivre l'évolution** des indicateurs

## 🔧 Variables d'Entrée

### Informations Personnelles
- **Âge** : Âge du client (18-100 ans)
- **Sexe** : Homme/Femme
- **Pays** : France/Allemagne/Espagne
- **Catégorie** : RUBIS/SILVER/GOLD/PLATINUM

### Informations Bancaires
- **Score de Crédit** : Score de crédit (300-900)
- **Ancienneté** : Nombre d'années depuis l'ouverture du compte (0-20)
- **Solde** : Solde du compte principal (0-300,000 €)
- **Salaire Estimé** : Salaire annuel estimé (0-300,000 €)
- **Nombre de Produits** : Produits bancaires utilisés (1-4)
- **Points Gagnés** : Points de fidélité (0-100,000)

### Comportement Client
- **Carte de Crédit** : Possède une carte de crédit (Oui/Non)
- **Membre Actif** : Utilise activement les services (Oui/Non)
- **Plainte** : A déposé une plainte récemment (Oui/Non)
- **Score de Satisfaction** : Satisfaction client (0-5)

## 🎯 Interprétation des Résultats

### Niveaux de Risque
- 🟢 **Faible** (< 30%) : Client fidèle, risque minimal
- 🟡 **Moyen** (30-70%) : Attention requise, actions préventives
- 🔴 **Élevé** (> 70%) : Risque critique, actions immédiates

### Actions Recommandées
- **Risque Faible** : Maintenir la relation client
- **Risque Moyen** : Proposer des offres personnalisées
- **Risque Élevé** : Contact immédiat, plan de rétention

## 🧪 Tests et Qualité

### Validation des Données
- Vérification des plages de valeurs
- Validation des règles métier
- Gestion des erreurs de saisie

### Logging
- Traçabilité des prédictions
- Monitoring des erreurs
- Debugging facilité

## ✅ Fonctionnalités Implémentées (Phase 1)

- [x] **Dashboard de métriques** avec visualisations interactives
- [x] **Export PDF** des rapports complets 
- [x] **Traitement par lots** via upload CSV
- [x] **Importance des features** et analytics avancés
- [x] **Interface multi-onglets** moderne
- [x] **Validation robuste** des données
- [x] **Gestion d'erreurs** complète

## 🔮 Améliorations Futures (Phases 2-4)

### 🥈 **Phase 2 - Court Terme**
- [ ] Base de données pour historique des prédictions
- [ ] SHAP values pour explainability détaillée  
- [ ] API REST pour intégrations externes
- [ ] Authentification et gestion des utilisateurs

### 🥉 **Phase 3 - Moyen Terme**
- [ ] Comparaison de modèles (XGBoost, LightGBM)
- [ ] Alertes automatiques en temps réel
- [ ] Clustering automatique des clients
- [ ] Interface mobile responsive

### 🏆 **Phase 4 - Long Terme**
- [ ] MLOps complet avec retraining automatique
- [ ] Recommandations IA intelligentes
- [ ] Intégrations CRM (Salesforce, HubSpot)
- [ ] Monitoring de la dérive des données

## 🐛 Résolution de Problèmes

### Erreur de Chargement du Modèle
```
❌ Erreur de prédiction : Modèle non trouvé
```
**Solution** : Vérifier que le fichier `models/random_forest_model.pkl` existe

### Erreur de Validation
```
❌ Erreurs de validation détectées
```
**Solution** : Vérifier que toutes les valeurs sont dans les plages autorisées

### Erreur d'Importation
```
ModuleNotFoundError: No module named 'config'
```
**Solution** : Lancer l'application depuis le répertoire racine du projet

## 👥 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
