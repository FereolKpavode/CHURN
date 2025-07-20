import streamlit as st
import pandas as pd
import joblib  # Pour charger ton modèle sauvegardé

# Charger ton modèle pré-entraîné (assure-toi que le fichier est dans le même dossier)
model = joblib.load("random_forest_model.pkl")

st.title("Prédiction de l'attrition des clients (Churn)")

# Exemple d'entrée utilisateur (à adapter selon tes variables)
age = st.number_input("Âge du client", min_value=18, max_value=100, value=30)
complain = st.selectbox("Le client a-t-il fait une plainte ?", ("Oui", "Non"))
num_of_products = st.number_input("Nombre de produits détenus", min_value=1, max_value=10, value=2)
is_active_member = st.selectbox("Le client est-il un membre actif ?", ("Oui", "Non"))
balance = st.number_input("Solde du compte", min_value=0.0, value=1000.0)

# Convertir les inputs en données exploitables par le modèle
data = {
    "age": age,
    "complain": 1 if complain == "Oui" else 0,
    "numofproducts": num_of_products,
    "isactivemember": 1 if is_active_member == "Oui" else 0,
    "balance": balance
}

input_df = pd.DataFrame([data])

if st.button("Prédire le churn"):
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0][1]

    if prediction == 1:
        st.error(f"Le client est susceptible de partir. Probabilité : {proba:.2f}")
    else:
        st.success(f"Le client est susceptible de rester. Probabilité : {proba:.2f}")
