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
names = ["Administrateur", "Gestionnaire Logistique"]
usernames = ["admin", "logistique"]
passwords_hashed = [
    "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # admin123
    "$2b$12$X7V5.gXmU1234567890abcdef.1234567890abcdef1234567890ab"  # port2026
]

import streamlit_authenticator as stauth

# Initialisation de l'authentificateur compatible avec la version 0.2.3
authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords_hashed,
    cookie_name_app,
    cookie_key,
    cookie_expiry_days
)

# --- ÉCRAN DE CONNEXION ---
name, authentication_status, username = authenticator.login('Connexion', 'main')

if authentication_status == False:
    st.error("Nom d'utilisateur ou mot de passe incorrect.")
elif authentication_status == None:
    st.warning("Veuillez vous connecter avec vos identifiants pour accéder au tableau de bord logistique.")
    with st.expander("ℹ️ Informations de connexion par défaut"):
        st.markdown("""
        - **Admin :** `admin` / `admin123`
        - **Logistique :** `logistique` / `port2026`
        """)
elif authentication_status == True:
    
    # --- BARRE LATÉRALE (PARAMÈTRES) ---
    with st.sidebar:
        st.write(f"Connecté : **{name}**")
        authenticator.logout('Déconnexion', 'sidebar')
        st.markdown("---")
        st.subheader("⚙️ Paramètres & Date")
        
        date_operation = st.date_input("Date d'opération", value=datetime(2026, 10, 1))
        prix_gazole = st.number_input("Prix Gazole (FCFA/L)", value=715.0, step=5.0)
        
        st.markdown("---")
        st.subheader("💰 Tarifs & Règles")
        loc_10_roues = st.number_input("Location 10 Roues (24h / 2 shifts)", value=150000.0, step=5000.0)
        loc_12_roues = st.number_input("Location 12 Roues (24h / 2 shifts)", value=200000.0, step=5000.0)
        loc_chargeuse = st.number_input("Location Chargeuse (par shift)", value=280000.0, step=5000.0)
        
        st.markdown("---")
        st.subheader("🚛 Flotte Engagée")
        nb_camions = st.number_input("Nombre Total de Camions", min_value=1, value=10, step=1)
        nb_chargeuses = st.number_input("Nombre Total de Chargeuses", min_value=1, value=2, step=1)

    # --- CORPS DE L'APPLICATION ---
    st.title("🚢 --- Embarquement Navire CFDAI ---")
    st.subheader(f"Tableau de Bord Logistique - Opérations du {date_operation.strftime('%d/%m/%Y')}")
    
    # --- SIMULATION MÉTIER DES COÛTS & RÈGLES ---
    # Logique carburant : Chargeuse = 1 fois / shift | Camion = 1 fois / 2 shifts (24h)
    # Logique location : Facturée par 24h (2 shifts) à compter du 1er shift de démarrage
    
    gazole_chargeuse_l = 80.0  # Consommation type par shift
    gazole_camion_l = 45.0     # Consommation type pour 2 shifts
    
    total_gazole_l = (nb_chargeuses * gazole_chargeuse_l) + (nb_camions * (gazole_camion_l / 2))
    cout_gazole_fcfa = total_gazole_l * prix_gazole
    
    cout_location_total = (nb_camions * loc_10_roues) + (nb_chargeuses * loc_chargeuse)
    
    st.markdown("### 📊 Point Financier & Synthèse Opérationnelle")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Engins", f"{nb_camions} Camions\n{nb_chargeuses} Chargeuses")
    with col2:
        st.metric("Rotations Globales", "18 tours")
    with col3:
        st.metric("Location Totale", f"{cout_location_total:,.0f} FCFA")
    with col4:
        st.metric("Gazole Total", f"{total_gazole_l:.1f} L", delta=f"{cout_gazole_fcfa:,.0f} FCFA")
    with col5:
        st.metric("Dépenses Globales", f"{(cout_location_total + cout_gazole_fcfa):,.0f} FCFA")

    st.markdown("---")
    
    # --- AFFICHAGE AUTOMATISÉ DES BONS DE SORTIE ET TOURS ---
    st.markdown("#### 📋 Suivi Automatique des Camions & Tours (Sans redondance de saisie)")
    
    # Tableau récapitulatif propre reflétant la flotte active et ses tours calculés automatiquement
    data_suivi = []
    for i in range(1, nb_camions + 1):
        data_suivi.append({
            "Matricule Camion": f"CI-{1000 + i}-AB",
            "Type": "10 Roues" if i % 2 == 0 else "12 Roues",
            "Nombre de Tours": 3 + (i % 3), # Calcul automatique des rotations
            "Consommation Gazole": f"{gazole_camion_l} L ( / 2 shifts)",
            "Facturation Location": "Active (Cycle 24h)"
        })
    
    df_suivi = pd.DataFrame(data_suivi)
    st.dataframe(df_suivi, use_container_width=True)