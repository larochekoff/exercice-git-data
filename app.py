"""
app.py: Application principale Streamlit pour le suivi opérationnel et financier
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config import SHIFT_JOUR, SHIFT_NUIT
from models import init_session_state
from services import BusinessLogic

# Configuration de la page
st.set_page_config(
    page_title="Suivi Opérationnel Flotte & Chantiers",
    page_icon="🏗️",
    layout="wide"
)

# Initialisation de l'état
init_session_state()

# ==========================================
# PANNEAU LATÉRAL : TARIFS ET PARAMÈTRES
# ==========================================
st.sidebar.title("⚙️ Paramètres & Tarifs")
st.sidebar.markdown("---")

st.sidebar.subheader("Tarif Carburant")
st.session_state.tarifs["carburant"] = st.sidebar.number_input(
    "Tarif carburant (FCFA / litre)", 
    min_value=0, 
    value=st.session_state.tarifs["carburant"], 
    step=25
)

st.sidebar.subheader("Montants de Location")
st.session_state.tarifs["loc_12_roues"] = st.sidebar.number_input(
    "Location 12 roues (par 2 shifts)", 
    min_value=0, 
    value=st.session_state.tarifs["loc_12_roues"], 
    step=5000
)
st.session_state.tarifs["loc_10_roues"] = st.sidebar.number_input(
    "Location 10 roues (par 2 shifts)", 
    min_value=0, 
    value=st.session_state.tarifs["loc_10_roues"], 
    step=5000
)
st.session_state.tarifs["loc_chargeuses"] = st.sidebar.number_input(
    "Location Chargeuses (par 2 shifts)", 
    min_value=0, 
    value=st.session_state.tarifs["loc_chargeuses"], 
    step=5000
)

st.sidebar.subheader("Personnel d'Entretien (par shift)")
st.session_state.tarifs["mo_jour"] = st.sidebar.number_input(
    "Shift Jour (8h - 19h)", 
    min_value=0, 
    value=st.session_state.tarifs["mo_jour"], 
    step=500
)
st.session_state.tarifs["mo_nuit"] = st.sidebar.number_input(
    "Shift Nuit (19h - 8h)", 
    min_value=0, 
    value=st.session_state.tarifs["mo_nuit"], 
    step=500
)

# ==========================================
# INTERFACE PRINCIPALE
# ==========================================
st.title("🚜 Suivi Opérationnel : Flotte, Chargeuses & Personnel")
st.markdown("Gestion des bons de sortie, des consommations de carburant, des locations (cycles 24h / 2 shifts) et des rapports.")

tab_saisie, tab_bons, tab_rapport_jour, tab_rapport_global = st.tabs([
    "📝 Saisie Opérationnelle", 
    "📋 Bons de Sortie & Suivi", 
    "📊 Rapport Journalier", 
    "📈 Rapport Global"
])

# --- ONGLET 1 : SAISIE OPÉRATIONNELLE ---
with tab_saisie:
    st.subheader("Enregistrement des Opérations par Shift")
    
    col_date, col_shift = st.columns(2)
    with col_date:
        date_operation = st.date_input("Date des opérations", value=datetime.today())
    with col_shift:
        shift_choisi = st.selectbox("Sélectionnez le Shift", [SHIFT_JOUR, SHIFT_NUIT])

    choix_type_saisie = st.radio("Type d'élément à enregistrer", ["Camion (10/12 roues)", "Chargeuse", "Personnel d'Entretien"], horizontal=True)

    if choix_type_saisie == "Camion (10/12 roues)":
        with st.form("form_camion"):
            st.markdown("### Saisie Camion")
            c_type = st.selectbox("Type de Camion", ["12 roues", "10 roues"])
            c_immat = st.text_input("Immatriculation / Coordonnées du Camion", placeholder="Ex: CI-1234-AB")
            c_tours = st.number_input("Nombre de tours effectués", min_value=1, value=1, step=1)
            
            # Règle carburant camions : pris 1 seule fois par deux shifts
            prend_carburant = st.checkbox("Prise de carburant pour ce shift (Règle : 1 fois / 2 shifts)")
            c_litres = 0.0
            if prend_carburant:
                c_litres = st.number_input("Volume de carburant (Litres)", min_value=0.0, value=50.0, step=5.0)

            submitted_c = st.form_submit_button("Enregistrer le Camion")
            if submitted_c:
                if not c_immat:
                    st.error("Veuillez renseigner les coordonnées du camion.")
                else:
                    tarif_carb = st.session_state.tarifs["carburant"]
                    cout_carb = c_litres * tarif_carb if prend_carburant else 0.0
                    
                    # Vérification location (tous les 2 shifts)
                    facturer_loc = BusinessLogic.verifier_et_appliquer_location_camion(
                        st.session_state.saisies_camions, c_immat, shift_choisi
                    )
                    montant_loc_base = st.session_state.tarifs["loc_12_roues"] if c_type == "12 roues" else st.session_state.tarifs["loc_10_roues"]
                    cout_loc = montant_loc_base if facturer_loc else 0.0

                    enregistrement = {
                        "Date": str(date_operation),
                        "Shift": shift_choisi,
                        "Type": c_type,
                        "Identifiant": c_immat,
                        "Tours": c_tours,
                        "Carburant_Litres": c_litres,
                        "Cout_Carburant": cout_carb,
                        "Location_Appliquee": "Oui (2 shifts)" if facturer_loc else "Non (Reporté)",
                        "Cout_Location": cout_loc
                    }
                    st.session_state.saisies_camions.append(enregistrement)
                    st.success(f"Camion {c_immat} enregistré avec succès pour le shift {shift_choisi} !")

    elif choix_type_saisie == "Chargeuse":
        with st.form("form_chargeuse"):
            st.markdown("### Saisie Chargeuse")
            ch_id = st.text_input("Identifiant / Numéro de la Chargeuse", placeholder="Ex: CHARG-01")
            
            # Règle carburant chargeuses : pris une seule fois par shift
            prend_carburant_ch = st.checkbox("Prise de carburant pour ce shift (Règle : 1 fois par shift)")
            ch_litres = 0.0
            if prend_carburant_ch:
                ch_litres = st.number_input("Volume de carburant (Litres)", min_value=0.0, value=40.0, step=5.0)

            submitted_ch = st.form_submit_button("Enregistrer la Chargeuse")
            if submitted_ch:
                if not ch_id:
                    st.error("Veuillez renseigner l'identifiant de la chargeuse.")
                else:
                    tarif_carb = st.session_state.tarifs["carburant"]
                    cout_carb = ch_litres * tarif_carb if prend_carburant_ch else 0.0

                    # Vérification location chargeuse (tous les 2 shifts)
                    facturer_loc_ch = BusinessLogic.verifier_et_appliquer_location_chargeuse(
                        st.session_state.saisies_chargeuses, ch_id
                    )
                    cout_loc_ch = st.session_state.tarifs["loc_chargeuses"] if facturer_loc_ch else 0.0

                    enregistrement_ch = {
                        "Date": str(date_operation),
                        "Shift": shift_choisi,
                        "Identifiant": ch_id,
                        "Carburant_Litres": ch_litres,
                        "Cout_Carburant": cout_carb,
                        "Location_Appliquee": "Oui (2 shifts)" if facturer_loc_ch else "Non (Reporté)",
                        "Cout_Location": cout_loc_ch
                    }
                    st.session_state.saisies_chargeuses.append(enregistrement_ch)
                    st.success(f"Chargeuse {ch_id} enregistrée pour le shift {shift_choisi} !")

    else:
        with st.form("form_personnel"):
            st.markdown("### Enregistrement Personnel d'Entretien")
            p_nom = st.text_input("Nom de l'équipe ou Agent / Référence", placeholder="Ex: Équipe Maintenance A")
            
            # Tarif automatique selon le shift choisi
            montant_mo = st.session_state.tarifs["mo_jour"] if shift_choisi == SHIFT_JOUR else st.session_state.tarifs["mo_nuit"]
            st.info(f"Tarif appliqué pour le shift {shift_choisi} : **{montant_mo:,.0f} FCFA**")

            submitted_p = st.form_submit_button("Enregistrer le Personnel")
            if submitted_p:
                if not p_nom:
                    st.error("Veuillez entrer une référence pour le personnel.")
                else:
                    enregistrement_p = {
                        "Date": str(date_operation),
                        "Shift": shift_choisi,
                        "Reference": p_nom,
                        "Montant_MO": montant_mo
                    }
                    st.session_state.saisies_personnel.append(enregistrement_p)
                    st.success(f"Personnel d'entretien enregistré pour le shift {shift_choisi} !")

# --- ONGLET 2 : BONS DE SORTIE & SUVI ---
with tab_bons:
    st.subheader("📋 Bons de Sortie et Suivi des Engins")
    st.markdown("Affichage des coordonnées, nombre de tours automatiques, carburant et statuts de location.")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("#### 🚚 Suivi Camions")
        if st.session_state.saisies_camions:
            df_c_view = pd.DataFrame(st.session_state.saisies_camions)
            st.dataframe(df_c_view, use_container_width=True)
        else:
            st.info("Aucun bon de sortie camion enregistré.")

    with col_b2:
        st.markdown("#### 🏗️ Suivi Chargeuses")
        if st.session_state.saisies_chargeuses:
            df_ch_view = pd.DataFrame(st.session_state.saisies_chargeuses)
            st.dataframe(df_ch_view, use_container_width=True)
        else:
            st.info("Aucun bon de sortie chargeuse enregistré.")

    st.markdown("#### 👷 Suivi Personnel d'Entretien")
    if st.session_state.saisies_personnel:
        df_p_view = pd.DataFrame(st.session_state.saisies_personnel)
        st.dataframe(df_p_view, use_container_width=True)
    else:
        st.info("Aucun enregistrement pour le personnel d'entretien.")

# --- ONGLET 3 : RAPPORT JOURNALIER ---
with tab_rapport_jour:
    st.subheader("📊 Rapport Journalier des Opérations")
    date_rapport = st.date_input("Sélectionner la date du rapport", value=datetime.today(), key="date_rep_jour")
    
    rapport_j = BusinessLogic.gerer_rapport_journalier(
        date_rapport, 
        st.session_state.saisies_camions, 
        st.session_state.saisies_chargeuses, 
        st.session_state.saisies_personnel
    )

    st.markdown(f"### Résultats pour la journée du : {date_rapport}")
    
    st.markdown("##### 1. Camions")
    if not rapport_j["camions"].empty:
        st.dataframe(rapport_j["camions"], use_container_width=True)
        total_carb_c = rapport_j["camions"]["Cout_Carburant"].sum()
        total_loc_c = rapport_j["camions"]["Cout_Location"].sum()
        st.metric("Total Carburant Camions", f"{total_carb_c:,.0f} FCFA")
        st.metric("Total Location Camions", f"{total_loc_c:,.0f} FCFA")
    else:
        st.info("Aucune donnée camions pour cette date.")

    st.markdown("##### 2. Chargeuses")
    if not rapport_j["chargeuses"].empty:
        st.dataframe(rapport_j["chargeuses"], use_container_width=True)
        total_carb_ch = rapport_j["chargeuses"]["Cout_Carburant"].sum()
        total_loc_ch = rapport_j["chargeuses"]["Cout_Location"].sum()
        st.metric("Total Carburant Chargeuses", f"{total_carb_ch:,.0f} FCFA")
        st.metric("Total Location Chargeuses", f"{total_loc_ch:,.0f} FCFA")
    else:
        st.info("Aucune donnée chargeuses pour cette date.")

    st.markdown("##### 3. Personnel d'Entretien")
    if not rapport_j["personnel"].empty:
        st.dataframe(rapport_j["personnel"], use_container_width=True)
        total_mo = rapport_j["personnel"]["Montant_MO"].sum()
        st.metric("Total Main d'Œuvre Entretien", f"{total_mo:,.0f} FCFA")
    else:
        st.info("Aucune donnée personnel pour cette date.")

# --- ONGLET 4 : RAPPORT GLOBAL ---
with tab_rapport_global:
    st.subheader("📈 Rapport Global de Fin des Opérations")
    st.markdown("Consolidation globale de l'ensemble des données enregistrées depuis le début.")

    rapport_g = BusinessLogic.gerer_rapport_global(
        st.session_state.saisies_camions, 
        st.session_state.saisies_chargeuses, 
        st.session_state.saisies_personnel
    )

    col_g1, col_g2, col_g3 = st.columns(3)
    
    sum_c_carb = rapport_g["camions"]["Cout_Carburant"].sum() if not rapport_g["camions"].empty else 0
    sum_c_loc = rapport_g["camions"]["Cout_Location"].sum() if not rapport_g["camions"].empty else 0
    with col_g1:
        st.metric("Total Camions", f"{sum_c_carb + sum_c_loc:,.0f} FCFA")

    sum_ch_carb = rapport_g["chargeuses"]["Cout_Carburant"].sum() if not rapport_g["chargeuses"].empty else 0
    sum_ch_loc = rapport_g["chargeuses"]["Cout_Location"].sum() if not rapport_g["chargeuses"].empty else 0
    with col_g2:
        st.metric("Total Chargeuses", f"{sum_ch_carb + sum_ch_loc:,.0f} FCFA")

    sum_mo = rapport_g["personnel"]["Montant_MO"].sum() if not rapport_g["personnel"].empty else 0
    with col_g3:
        st.metric("Total Personnel Entretien", f"{sum_mo:,.0f} FCFA")

    tot_general = sum_c_carb + sum_c_loc + sum_ch_carb + sum_ch_loc + sum_mo
    st.markdown("---")
    st.markdown(f"### 💰 Coût Total Global des Opérations : **{tot_general:,.0f} FCFA**")

    st.markdown("#### Historique Global Détaillé")
    with st.expander("Voir tous les camions"):
        if not rapport_g["camions"].empty:
            st.dataframe(rapport_g["camions"], use_container_width=True)
        else:
            st.write("Vide")

    with st.expander("Voir toutes les chargeuses"):
        if not rapport_g["chargeuses"].empty:
            st.dataframe(rapport_g["chargeuses"], use_container_width=True)
        else:
            st.write("Vide")

    with st.expander("Voir tout le personnel"):
        if not rapport_g["personnel"].empty:
            st.dataframe(rapport_g["personnel"], use_container_width=True)
        else:
            st.write("Vide")