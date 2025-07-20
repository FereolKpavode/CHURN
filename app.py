import streamlit as st
import pandas as pd
import joblib

# Chargement du modèle
model = joblib.load("random_forest_model.pkl")

st.title("Prédiction de l'attrition des clients (Churn)")

# Interface utilisateur
creditscore = st.number_input("Credit Score", 300, 900, 600)
age = st.number_input("Âge", 18, 100, 30)
tenure = st.slider("Ancienneté (tenure)", 0, 20, 3)
balance = st.number_input("Solde", 0.0, 300000.0, 1000.0)
numofproducts = st.slider("Nombre de produits", 1, 4, 2)
hascrcard = st.selectbox("A une carte de crédit ?", ["Oui", "Non"])
isactivemember = st.selectbox("Est un membre actif ?", ["Oui", "Non"])
estimatedsalary = st.number_input("Salaire estimé", 0.0, 300000.0, 50000.0)
complain = st.selectbox("A fait une plainte ?", ["Oui", "Non"])
satisfaction_score = st.slider("Score de satisfaction", 0, 5, 3)
point_earned = st.number_input("Points gagnés", 0, 100000, 500)

gender = st.selectbox("Sexe", ["Homme", "Femme"])
country = st.selectbox("Pays", ["France", "Allemagne", "Espagne"])
category = st.selectbox("Catégorie", ["RUBIS", "SILVER", "GOLD", "PLATINUM"])

# Encodage
input_data = {
    'creditscore': creditscore,
    'age': age,
    'tenure': tenure,
    'balance': balance,
    'numofproducts': numofproducts,
    'hascrcard': 1 if hascrcard == "Oui" else 0,
    'isactivemember': 1 if isactivemember == "Oui" else 0,
    'estimatedsalary': estimatedsalary,
    'complain': 1 if complain == "Oui" else 0,
    'satisfaction score': satisfaction_score,
    'point earned': point_earned,
    'Male': 1 if gender == "Homme" else 0,
    'Germany': 1 if country == "Allemagne" else 0,
    'Spain': 1 if country == "Espagne" else 0,
    'GOLD': 1 if category == "GOLD" else 0,
    'PLATINUM': 1 if category == "PLATINUM" else 0,
    'SILVER': 1 if category == "SILVER" else 0
    # RUBIS est implicite si les trois autres sont à 0
}

# Prédiction
if st.button("Prédire le churn"):
    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0][1]

    if prediction == 1:
        st.error(f"⚠️ Le client est susceptible de **partir**. Probabilité : {proba:.2f}")
    else:
        st.success(f"✅ Le client est susceptible de **rester**. Probabilité : {proba:.2f}")
