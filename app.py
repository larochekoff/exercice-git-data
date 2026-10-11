"""
app.py: Application de Suivi Opérationnel et Financier - CFDAI
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURATION ET CONSTANTES
# ==========================================
SHIFT_JOUR = "Shift Jour (8h - 19h)"
SHIFT_NUIT = "Shift Nuit (19h - 8h)"

st.set_page_config(
    page_title="CFDAI - Suivi Opérationnel Flotte & Chantiers",
    page_icon="🏗️",
    layout="wide"
)

# ==========================================
# 2. INITIALISATION DE L'ÉTAT DE SESSION
# ==========================================
if "tarifs" not in st.session_state:
    st.session_state.tarifs = {
        "carburant": 750,
        "loc_12_roues": 150000,
        "loc_10_roues": 120000,
        "loc_chargeuses": 100000,
        "mo_jour": 5000,
        "mo_nuit": 6000
    }

# Stockage des journaux bruts par shift pour les rapports par shift et globaux
if "historique_shifts" not in st.session_state:
    st.session_state.historique_shifts = []

# Stockage consolidé par engin (pour éviter la redondance et cumuler les tours/carburant/location)
if "camions_actifs" not in st.session_state:
    st.session_state.camions_actifs = {} # {matricule: {type, tours, total_litres, cout_carb, cout_loc, shifts_count}}

if "chargeuses_actives" not in st.session_state:
    st.session_state.chargeuses_actives = {} # {id: {conducteur, total_litres, cout_carb, cout_loc, shifts_count}}

if "personnel_actifs" not in st.session_state:
    st.session_state.personnel_actifs = []

# ==========================================
# 3. PANNEAU LATÉRAL : STRUCTURE CFDAI & TARIFS
# ==========================================
st.sidebar.title("🏗️ Structure CFDAI")
st.sidebar.markdown("**Système de Suivi Opérationnel**")
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Paramètres & Tarifs")

st.session_state.tarifs["carburant"] = st.sidebar.number_input(
    "Tarif carburant (FCFA / litre)", min_value=0, value=st.session_state.tarifs["carburant"], step=25
)
st.session_state.tarifs["loc_12_roues"] = st.sidebar.number_input(
    "Location 12 roues (2 shifts)", min_value=0, value=st.session_state.tarifs["loc_12_roues"], step=5000
)
st.session_state.tarifs["loc_10_roues"] = st.sidebar.number_input(
    "Location 10 roues (2 shifts)", min_value=0, value=st.session_state.tarifs["loc_10_roues"], step=5000
)
st.session_state.tarifs["loc_chargeuses"] = st.sidebar.number_input(
    "Location Chargeuses (2 shifts)", min_value=0, value=st.session_state.tarifs["loc_chargeuses"], step=5000
)
st.session_state.tarifs["mo_jour"] = st.sidebar.number_input(
    "Main d'œuvre Shift Jour", min_value=0, value=st.session_state.tarifs["mo_jour"], step=500
)
st.session_state.tarifs["mo_nuit"] = st.sidebar.number_input(
    "Main d'œuvre Shift Nuit", min_value=0, value=st.session_state.tarifs["mo_nuit"], step=500
)

# ==========================================
# 4. INTERFACE PRINCIPALE
# ==========================================
st.title("🚜 CFDAI - Tableau de Bord Opérationnel")
st.markdown("Gestion consolidée des camions, chargeuses, personnel d'entretien, cycles de 24h et rapports par shift.")

tab_saisie, tab_bons, tab_rapport_shift, tab_rapport_global = st.tabs([
    "📝 Saisie Opérationnelle", 
    "📋 Historique Unique par Engin", 
    "📊 Rapport par Shift", 
    "📈 Rapport Global des Shifts"
])

# --- ONGLET 1 : SAISIE OPÉRATIONNELLE ---
with tab_saisie:
    st.subheader("Enregistrement des Opérations")
    
    col_d, col_s = st.columns(2)
    with col_d:
        date_op = st.date_input("Date", value=datetime.today())
    with col_s:
        shift_op = st.selectbox("Sélectionnez le Shift de départ", [SHIFT_JOUR, SHIFT_NUIT])

    type_saisie = st.radio("Élément à enregistrer", ["Camion", "Chargeuse", "Personnel d'Entretien"], horizontal=True)

    if type_saisie == "Camion":
        with st.form("form_camion"):
            c_type = st.selectbox("Type de Camion", ["12 roues", "10 roues"])
            c_immat = st.text_input("Matricule / Immatriculation du Camion", placeholder="Ex: CI-1234-AB")
            c_tours = st.number_input("Nombre de tours effectués", min_value=1, value=1, step=1)
            
            prend_carb = st.checkbox("Prise de carburant pour ce shift (Règle : 1 fois / 2 shifts)")
            c_litres = 0.0
            if prend_carb:
                c_litres = st.number_input("Volume de carburant (Litres)", min_value=0.0, value=50.0, step=5.0)

            submitted_c = st.form_submit_button("Enregistrer le Camion")
            if submitted_c:
                if not c_immat.strip():
                    st.error("Veuillez renseigner le matricule du camion.")
                else:
                    immat = c_immat.strip()
                    tarif_c = st.session_state.tarifs["carburant"]
                    
                    # Gestion de l'historique unique par camion
                    if immat not in st.session_state.camions_actifs:
                        st.session_state.camions_actifs[immat] = {
                            "Type": c_type,
                            "Matricule": immat,
                            "Tours": 0,
                            "Litres_Carburant": 0.0,
                            "Cout_Carburant": 0.0,
                            "Cout_Location": 0.0,
                            "Shifts_Count": 0
                        }
                    
                    cam = st.session_state.camions_actifs[immat]
                    cam["Tours"] += c_tours
                    cam["Shifts_Count"] += 1
                    
                    # Carburant pris une seule fois tous les 2 shifts
                    if prend_carb:
                        cam["Litres_Carburant"] += c_litres
                        cam["Cout_Carburant"] += c_litres * tarif_c
                    
                    # Location facturée tous les 2 shifts (commençant au 1er shift)
                    montant_loc_base = st.session_state.tarifs["loc_12_roues"] if c_type == "12 roues" else st.session_state.tarifs["loc_10_roues"]
                    if cam["Shifts_Count"] % 2 == 1: # 1er shift du cycle de 2
                        cam["Cout_Location"] += montant_loc_base

                    # Enregistrement pour le rapport du shift
                    st.session_state.historique_shifts.append({
                        "Date": str(date_op),
                        "Shift": shift_op,
                        "Categorie": "Camion",
                        "Identifiant": immat,
                        "Details": f"{c_type} - {c_tours} tours",
                        "Cout": (c_litres * tarif_c if prend_carb else 0) + (montant_loc_base if cam["Shifts_Count"] % 2 == 1 else 0)
                    })
                    st.success(f"Camion {immat} mis à jour avec succès !")

    elif type_saisie == "Chargeuse":
        with st.form("form_chargeuse"):
            ch_id = st.text_input("Identifiant de la Chargeuse", placeholder="Ex: CHARG-01")
            ch_conducteur = st.text_input("Nom du conducteur", placeholder="Ex: Kouassi Jean")
            
            prend_carb_ch = st.checkbox("Prise de carburant pour ce shift")
            ch_litres = 0.0
            if prend_carb_ch:
                ch_litres = st.number_input("Volume de carburant (Litres)", min_value=0.0, value=40.0, step=5.0)

            submitted_ch = st.form_submit_button("Enregistrer la Chargeuse")
            if submitted_ch:
                if not ch_id.strip():
                    st.error("Veuillez renseigner l'identifiant de la chargeuse.")
                else:
                    cid = ch_id.strip()
                    tarif_c = st.session_state.tarifs["carburant"]

                    if cid not in st.session_state.chargeuses_actives:
                        st.session_state.chargeuses_actives[cid] = {
                            "Identifiant": cid,
                            "Conducteur": ch_conducteur,
                            "Litres_Carburant": 0.0,
                            "Cout_Carburant": 0.0,
                            "Cout_Location": 0.0,
                            "Shifts_Count": 0
                        }
                    
                    ch = st.session_state.chargeuses_actives[cid]
                    ch["Conducteur"] = ch_conducteur
                    ch["Shifts_Count"] += 1

                    if prend_carb_ch:
                        ch["Litres_Carburant"] += ch_litres
                        ch["Cout_Carburant"] += ch_litres * tarif_c

                    montant_loc_ch = st.session_state.tarifs["loc_chargeuses"]
                    if ch["Shifts_Count"] % 2 == 1:
                        ch["Cout_Location"] += montant_loc_ch

                    st.session_state.historique_shifts.append({
                        "Date": str(date_op),
                        "Shift": shift_op,
                        "Categorie": "Chargeuse",
                        "Identifiant": cid,
                        "Details": f"Conducteur: {ch_conducteur}",
                        "Cout": (ch_litres * tarif_c if prend_carb_ch else 0) + (montant_loc_ch if ch["Shifts_Count"] % 2 == 1 else 0)
                    })
                    st.success(f"Chargeuse {cid} mise à jour avec succès !")

    else:
        with st.form("form_personnel"):
            p_agents = st.number_input("Nombre d'agents présents", min_value=0, value=5, step=1)
            p_absences = st.number_input("Nombre d'absences", min_value=0, value=0, step=1)
            
            tarif_mo = st.session_state.tarifs["mo_jour"] if shift_op == SHIFT_JOUR else st.session_state.tarifs["mo_nuit"]
            st.info(f"Tarif unitaire appliqué ({shift_op}) : {tarif_mo:,.0f} FCFA par agent présent.")

            submitted_p = st.form_submit_button("Enregistrer le Personnel")
            if submitted_p:
                total_mo = p_agents * tarif_mo
                st.session_state.personnel_actifs.append({
                    "Date": str(date_op),
                    "Shift": shift_op,
                    "Agents_Presents": p_agents,
                    "Absences": p_absences,
                    "Montant_MO": total_mo
                })
                st.session_state.historique_shifts.append({
                    "Date": str(date_op),
                    "Shift": shift_op,
                    "Categorie": "Personnel",
                    "Identifiant": "Équipe Entretien",
                    "Details": f"Présents: {p_agents}, Absents: {p_absences}",
                    "Cout": total_mo
                })
                st.success("Personnel d'entretien enregistré avec succès !")

# --- ONGLET 2 : HISTORIQUE UNIQUE PAR ENGIN ---
with tab_bons:
    st.subheader("📋 Historique Unique par Engin (Sans Redondance)")

    st.markdown("#### 🚚 Camions (Tours cumulés & Carburant/Location par cycles)")
    if st.session_state.camions_actifs:
        df_cam = pd.DataFrame(list(st.session_state.camions_actifs.values()))
        st.dataframe(df_cam, use_container_width=True)
    else:
        st.info("Aucun camion enregistré.")

    st.markdown("#### 🏗️ Chargeuses (Conducteur, Carburant & Location)")
    if st.session_state.chargeuses_actives:
        df_ch = pd.DataFrame(list(st.session_state.chargeuses_actives.values()))
        st.dataframe(df_ch, use_container_width=True)
    else:
        st.info("Aucune chargeuse enregistrée.")

    st.markdown("#### 👷 Personnel d'Entretien")
    if st.session_state.personnel_actifs:
        df_pers = pd.DataFrame(st.session_state.personnel_actifs)
        st.dataframe(df_pers, use_container_width=True)
    else:
        st.info("Aucun historique personnel enregistré.")

# --- ONGLET 3 : RAPPORT PAR SHIFT ---
with tab_rapport_shift:
    st.subheader("📊 Rapport Détaillé par Shift")
    
    c_rep_date, c_rep_shift = st.columns(2)
    with c_rep_date:
        sel_date = st.date_input("Date du rapport", value=datetime.today(), key="rep_date")
    with c_rep_shift:
        sel_shift = st.selectbox("Shift concerné", [SHIFT_JOUR, SHIFT_NUIT], key="rep_shift")

    df_hist = pd.DataFrame(st.session_state.historique_shifts)
    if not df_hist.empty and "Date" in df_hist.columns and "Shift" in df_hist.columns:
        df_shift_filtered = df_hist[(df_hist["Date"] == str(sel_date)) & (df_hist["Shift"] == sel_shift)]
        
        st.markdown(f"##### Activités du {sel_date} - {sel_shift}")
        if not df_shift_filtered.empty:
            st.dataframe(df_shift_filtered, use_container_width=True)
            total_shift_cout = df_shift_filtered["Cout"].sum()
            st.metric("Coût Total pour ce Shift", f"{total_shift_cout:,.0f} FCFA")
        else:
            st.info("Aucune opération enregistrée pour ce shift précis.")
    else:
        st.info("Aucune donnée disponible pour le moment.")

# --- ONGLET 4 : RAPPORT GLOBAL DES SHIFTS ---
with tab_rapport_global:
    st.subheader("📈 Rapport Global de Toutes les Opérations (CFDAI)")
    
    # Calculs globaux consolidés camions
    total_tours_glob = sum(c["Tours"] for c in st.session_state.camions_actifs.values()) if st.session_state.camions_actifs else 0
    total_carb_cam = sum(c["Cout_Carburant"] for c in st.session_state.camions_actifs.values()) if st.session_state.camions_actifs else 0
    total_loc_cam = sum(c["Cout_Location"] for c in st.session_state.camions_actifs.values()) if st.session_state.camions_actifs else 0

    # Calculs globaux consolidés chargeuses
    total_carb_ch = sum(ch["Cout_Carburant"] for ch in st.session_state.chargeuses_actives.values()) if st.session_state.chargeuses_actives else 0
    total_loc_ch = sum(ch["Cout_Location"] for ch in st.session_state.chargeuses_actives.values()) if st.session_state.chargeuses_actives else 0

    # Calculs globaux personnel
    total_mo_glob = sum(p["Montant_MO"] for p in st.session_state.personnel_actifs) if st.session_state.personnel_actifs else 0

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.metric("Total Tours Camions", f"{total_tours_glob} tours")
        st.metric("Coût Carburant Camions", f"{total_carb_cam:,.0f} FCFA")
        st.metric("Location Camions", f"{total_loc_cam:,.0f} FCFA")
    with col_g2:
        st.metric("Coût Carburant Chargeuses", f"{total_carb_ch:,.0f} FCFA")
        st.metric("Location Chargeuses", f"{total_loc_ch:,.0f} FCFA")
    with col_g3:
        st.metric("Total Main d'Œuvre Entretien", f"{total_mo_glob:,.0f} FCFA")

    cout_total_global = total_carb_cam + total_loc_cam + total_carb_ch + total_loc_ch + total_mo_glob
    st.markdown("---")
    st.markdown(f"### 💰 Coût Total Global de l'Opération CFDAI : **{cout_total_global:,.0f} FCFA**")