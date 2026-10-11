import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Embarquement Navire CFDAI",
    page_icon="🚢",
    layout="wide"
)

# --- CONFIGURATION DES UTILISATEURS POUR L'AUTHENTIFICATION ---
credentials = {
    'usernames': {
        'admin': {
            'name': 'Administrateur',
            'password': '111'
        },
        'logistique': {
            'name': 'Gestionnaire Logistique',
            'password': '222'
        },
        'comptabilite': {
            'name': 'Comptabilité',
            'password': '333'
        }
    }
}

cookie_name = "navire_auth_cookie"
cookie_key = "cle_secrete_super_securisee"
cookie_expiry_days = 30

# --- INITIALISATION DE LA AUTHENTIFICATION ---
authenticator = stauth.Authenticate(
    credentials,
    cookie_name,
    cookie_key,
    cookie_expiry_days
)

# --- ÉCRAN DE CONNEXION ---
name, authentication_status, username = authenticator.login('Connexion', 'main')

if authentication_status == False:
    st.error("Nom d'utilisateur ou mot de passe incorrect")
elif authentication_status == None:
    st.warning("Veuillez entrer vos identifiants de connexion")
elif authentication_status == True:
    # --- INTERFACE PRINCIPALE DE L'APPLICATION ---
    authenticator.LogoutButton('Déconnexion', 'sidebar')
    st.sidebar.success(f"Bienvenue {name} !")
    
    st.title("🚢 Gestion de l'Embarquement Navire - CFDAI")
    st.write("Bienvenue sur l'application de suivi et de gestion logistique.")
    
    # Ajoutez ici le reste de votre code métier (tableaux, formulaires, etc.)
    
    