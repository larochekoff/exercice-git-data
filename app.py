"""
app.py: Application de Suivi Opérationnel et Financier - CFDAI (Sans N° de bon pour les chargeuses)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Imports ReportLab pour la génération des PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. CONFIGURATION ET CONSTANTES
# ==========================================
SHIFT_JOUR = "Shift 08h - 19h"
SHIFT_NUIT = "Shift 19h - 08h"

st.set_page_config(
    page_title="CFDAI - Suivi Opérationnel Flotte & Chantiers",
    page_icon="🏗️",
    layout="wide"
)

# ==========================================
# 2. INITIALISATION ROBUSTE DE L'ÉTAT DE SESSION
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

if "historique_bons" not in st.session_state:
    st.session_state.historique_bons = []

if "personnel_actifs" not in st.session_state:
    st.session_state.personnel_actifs = []

# ==========================================
# 3. FONCTIONS DE GÉNÉRATION DES PDF
# ==========================================
def generer_pdf_shift(date_str, shift_str, df_shift):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1B365D'), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#555555'), alignment=1)
    
    elements.append(Paragraph("STRUCTURE CFDAI - RAPPORT DE SHIFT", title_style))
    elements.append(Paragraph(f"Date : {date_str} | Shift : {shift_str}", subtitle_style))
    elements.append(Spacer(1, 15))
    
    if not df_shift.empty:
        cols_to_show = [c for c in ["Categorie", "Identifiant", "Conducteur", "Numero_Bon", "Litres_Carburant", "Cout_Total"] if c in df_shift.columns]
        table_data = [cols_to_show] + df_shift[cols_to_show].astype(str).values.tolist()
        
        t = Table(table_data, colWidths=[100, 100, 100, 80, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F2F2')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))
        total_cout = df_shift["Cout_Total"].sum()
        elements.append(Paragraph(f"<b>Coût Total du Shift :</b> {total_cout:,.0f} FCFA", styles['Normal']))
    else:
        elements.append(Paragraph("Aucune opération enregistrée pour ce shift.", styles['Normal']))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generer_pdf_global(df_all):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1B365D'), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#555555'), alignment=1)
    
    elements.append(Paragraph("STRUCTURE CFDAI - RAPPORT GLOBAL DES OPÉRATIONS", title_style))
    elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 15))
    
    if not df_all.empty:
        camions_g = df_all[df_all["Categorie"] == "Camion"]
        chargeuses_g = df_all[df_all["Categorie"] == "Chargeuse"]
        personnel_g = df_all[df_all["Categorie"] == "Personnel"]

        tot_carb_cam = camions_g["Cout_Carburant"].sum() if not camions_g.empty else 0
        tot_loc_cam = camions_g["Cout_Location"].sum() if not camions_g.empty else 0
        tot_carb_ch = chargeuses_g["Cout_Carburant"].sum() if not chargeuses_g.empty else 0
        tot_loc_ch = chargeuses_g["Cout_Location"].sum() if not chargeuses_g.empty else 0
        tot_mo = personnel_g["Cout_Total"].sum() if not personnel_g.empty else 0
        tot_global = tot_carb_cam + tot_loc_cam + tot_carb_ch + tot_loc_ch + tot_mo

        recap_data = [
            ["Catégorie / Poste", "Montant Total (FCFA)"],
            ["Carburant Camions", f"{tot_carb_cam:,.0f}"],
            ["Location Camions", f"{tot_loc_cam:,.0f}"],
            ["Carburant Chargeuses", f"{tot_carb_ch:,.0f}"],
            ["Location Chargeuses", f"{tot_loc_ch:,.0f}"],
            ["Main d'Œuvre Entretien", f"{tot_mo:,.0f}"],
            ["TOTAL GÉNÉRAL", f"{tot_global:,.0f}"]
        ]
        
        t = Table(recap_data, colWidths=[250, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9E1E8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("Aucune donnée globale disponible.", styles['Normal']))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# 4. PANNEAU LATÉRAL : STRUCTURE CFDAI & TARIFS
# ==========================================
st.sidebar.title("🏗️ Structure CFDAI")
st.sidebar.markdown("**Système de Suivi Opérationnel**")
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Paramètres & Tarifs")

st.session_state.tarifs["carburant"] = st.sidebar.number_input(
    "Tarif carburant standard (FCFA / litre)", min_value=0, value=st.session_state.tarifs["carburant"], step=25
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
    "Main d'œuvre Shift 08h-19h", min_value=0, value=st.session_state.tarifs["mo_jour"], step=500
)
st.session_state.tarifs["mo_nuit"] = st.sidebar.number_input(
    "Main d'œuvre Shift 19h-08h", min_value=0, value=st.session_state.tarifs["mo_nuit"], step=500
)

# ==========================================
# 5. INTERFACE PRINCIPALE
# ==========================================
st.title("🚜 CFDAI - Tableau de Bord Opérationnel")
st.markdown("Gestion consolidée, numérotation des bons, modifications, historique et export PDF imprimable.")

tab_saisie, tab_modif, tab_bons, tab_rapport_shift, tab_rapport_global = st.tabs([
    "📝 Saisie Opérationnelle", 
    "✏️ Modifier une Saisie",
    "📋 Historique des Engins & Bons", 
    "📊 Rapport par Shift", 
    "📈 Rapport Global des Shifts"
])

# --- ONGLET 1 : SAISIE OPÉRATIONNELLE ---
with tab_saisie:
    st.subheader("Enregistrement des Opérations")
    
    date_op = st.date_input("Date de l'opération", value=datetime.today())
    type_saisie = st.radio("Type d'élément à enregistrer", ["Camion", "Chargeuse", "Personnel d'Entretien"], horizontal=True)

    if type_saisie == "Camion":
        with st.form("form_camion"):
            shift_camion = st.selectbox("Sélectionnez le Shift", [SHIFT_JOUR, SHIFT_NUIT], key="shift_c")
            c_type = st.selectbox("Type de Camion", ["12 roues", "10 roues"])
            c_immat = st.text_input("Matricule / Immatriculation du Camion", placeholder="Ex: CI-1234-AB")
            c_num_bon = st.text_input("Numéro du Bon de Sortie", placeholder="Ex: BON-001")
            
            camions_precedents = [b for b in st.session_state.historique_bons if b.get("Categorie") == "Camion" and b.get("Identifiant") == c_immat.strip().upper()]
            dernier_shift_carburant_autorise = True
            if camions_precedents:
                dernier_bon = camions_precedents[-1]
                if dernier_bon.get("Litres_Carburant", 0.0) > 0:
                    dernier_shift_carburant_autorise = False

            st.markdown("---")
            if dernier_shift_carburant_autorise:
                prend_carb = st.checkbox("Prise de carburant pour ce shift (Autorisé - 1er shift du cycle)", value=True)
            else:
                prend_carb = st.checkbox("Prise de carburant pour ce shift (Bloqué - Carburant déjà pris au shift précédent)", value=False, disabled=True)

            c_litres = 0.0
            if prend_carb and dernier_shift_carburant_autorise:
                c_litres = st.number_input("Volume de carburant (Litres) - Ajustable", min_value=0.0, value=50.0, step=5.0)

            submitted_c = st.form_submit_button("Enregistrer le Bon Camion")
            if submitted_c:
                if not c_immat.strip() or not c_num_bon.strip():
                    st.error("Veuillez renseigner le matricule et le numéro de bon de sortie.")
                else:
                    immat = c_immat.strip().upper()
                    num_bon = c_num_bon.strip()
                    tarif_c = st.session_state.tarifs["carburant"]
                    
                    cout_carb = c_litres * tarif_c if (prend_carb and dernier_shift_carburant_autorise) else 0.0
                    litres_effectifs = c_litres if (prend_carb and dernier_shift_carburant_autorise) else 0.0

                    nb_bons_camion = len(camions_precedents)
                    montant_loc_base = st.session_state.tarifs["loc_12_roues"] if c_type == "12 roues" else st.session_state.tarifs["loc_10_roues"]
                    cout_loc = montant_loc_base if (nb_bons_camion % 2 == 0) else 0.0

                    enregistrement_bon = {
                        "ID_Unique": f"CAM-{immat}-{num_bon}-{datetime.now().strftime('%H%M%S')}",
                        "Date": str(date_op),
                        "Shift": shift_camion,
                        "Categorie": "Camion",
                        "Type_Camion": c_type,
                        "Identifiant": immat,
                        "Numero_Bon": num_bon,
                        "Litres_Carburant": litres_effectifs,
                        "Cout_Carburant": cout_carb,
                        "Cout_Location": cout_loc,
                        "Cout_Total": cout_carb + cout_loc
                    }
                    st.session_state.historique_bons.append(enregistrement_bon)
                    st.success(f"Bon camion n°{num_bon} enregistré pour le véhicule {immat} !")

    elif type_saisie == "Chargeuse":
        with st.form("form_chargeuse"):
            shift_chargeuse = st.selectbox("Sélectionnez le Shift", [SHIFT_JOUR, SHIFT_NUIT], key="shift_ch")
            ch_conducteur = st.text_input("Nom du conducteur de la Chargeuse", placeholder="Ex: Kouassi Jean")
            
            prend_carb_ch = st.checkbox("Prise de carburant pour ce shift (Comptabilisé 1 fois par shift)", value=True)
            ch_litres = 0.0
            if prend_carb_ch:
                ch_litres = st.number_input("Volume de carburant (Litres) - Ajustable", min_value=0.0, value=40.0, step=5.0)

            submitted_ch = st.form_submit_button("Enregistrer la Chargeuse")
            if submitted_ch:
                if not ch_conducteur.strip():
                    st.error("Veuillez renseigner le nom du conducteur.")
                else:
                    conducteur = ch_conducteur.strip().title()
                    tarif_c = st.session_state.tarifs["carburant"]

                    cout_carb_ch = ch_litres * tarif_c if prend_carb_ch else 0.0
                    conducteur_bons = [b for b in st.session_state.historique_bons if b.get("Categorie") == "Chargeuse" and b.get("Conducteur")] == conducteur]
                    montant_loc_ch = st.session_state.tarifs["loc_chargeuses"] if (len(conducteur_bons) % 2 == 0) else 0.0

                    enregistrement_ch = {
                        "ID_Unique": f"CH-{conducteur}-{datetime.now().strftime('%H%M%S%f')}",
                        "Date": str(date_op),
                        "Shift": shift_chargeuse,
                        "Categorie": "Chargeuse",
                        "Conducteur": conducteur,
                        "Numero_Bon": "N/A",
                        "Litres_Carburant": ch_litres if prend_carb_ch else 0.0,
                        "Cout_Carburant": cout_carb_ch,
                        "Cout_Location": montant_loc_ch,
                        "Cout_Total": cout_carb_ch + montant_loc_ch
                    }
                    st.session_state.historique_bons.append(enregistrement_ch)
                    st.success(f"Intervention chargeuse enregistrée pour le conducteur {conducteur} !")

    else:
        with st.form("form_personnel"):
            shift_pers = st.selectbox("Sélectionnez le Shift", [SHIFT_JOUR, SHIFT_NUIT], key="shift_p")
            p_agents = st.number_input("Nombre d'agents présents", min_value=0, value=5, step=1)
            p_absences = st.number_input("Nombre d'absences", min_value=0, value=0, step=1)
            
            tarif_mo = st.session_state.tarifs["mo_jour"] if shift_pers == SHIFT_JOUR else st.session_state.tarifs["mo_nuit"]
            st.info(f"Tarif unitaire appliqué ({shift_pers}) : {tarif_mo:,.0f} FCFA par agent présent.")

            submitted_p = st.form_submit_button("Enregistrer le Personnel")
            if submitted_p:
                total_mo = p_agents * tarif_mo
                enregistrement_p = {
                    "ID_Unique": f"MO-{datetime.now().strftime('%H%M%S')}",
                    "Date": str(date_op),
                    "Shift": shift_pers,
                    "Categorie": "Personnel",
                    "Identifiant": "Équipe Entretien",
                    "Agents_Presents": p_agents,
                    "Absences": p_absences,
                    "Cout_Total": total_mo
                }
                st.session_state.historique_bons.append(enregistrement_p)
                st.success("Personnel d'entretien enregistré avec succès !")

# --- ONGLET 2 : MODIFICATION EN CAS D'ERREUR ---
with tab_modif:
    st.subheader("✏️ Modification ou Suppression d'une Saisie Erronée")
    if st.session_state.historique_bons:
        df_all = pd.DataFrame(st.session_state.historique_bons)
        bon_ids = df_all["ID_Unique"].tolist()
        bon_a_modifier = st.selectbox("Sélectionner l'opération à modifier/supprimer (par ID)", bon_ids)
        
        selected_record = next((b for b in st.session_state.historique_bons if b["ID_Unique"] == bon_a_modifier), None)
        
        if selected_record:
            st.write(selected_record)
            if st.button("🗑️ Supprimer cette entrée"):
                st.session_state.historique_bons = [b for b in st.session_state.historique_bons if b["ID_Unique"] != bon_a_modifier]
                st.success("Entrée supprimée avec succès !")
                st.rerun()
    else:
        st.info("Aucun enregistrement disponible.")

# --- ONGLET 3 : HISTORIQUE DES ENGINS & BONS ---
with tab_bons:
    st.subheader("📋 Historique Global des Bons et Suivi des Engins")

    if st.session_state.historique_bons:
        df_historique = pd.DataFrame(st.session_state.historique_bons)
        
        st.markdown("#### 🚚 Historique Camions")
        camions_bons = df_historique[df_historique["Categorie"] == "Camion"]
        if not camions_bons.empty:
            camions_resume = camions_bons.groupby("Identifiant").agg(
                Type_Camion=("Type_Camion", "first"),
                Nombre_Tours=("Numero_Bon", "count"),
                Total_Litres_Gasoil=("Litres_Carburant", "sum"),
                Total_Cout_Carburant=("Cout_Carburant", "sum"),
                Total_Cout_Location=("Cout_Location", "sum"),
                Montant_Total_Du=("Cout_Total", "sum")
            ).reset_index()
            st.dataframe(camions_resume, use_container_width=True)
        else:
            st.info("Aucun bon camion enregistré.")

        st.markdown("#### 🏗️ Historique Chargeuses (Par Conducteur)")
        chargeuses_bons = df_historique[df_historique["Categorie"] == "Chargeuse"]
        if not chargeuses_bons.empty:
            chargeuses_resume = chargeuses_bons.groupby("Conducteur").agg(
                Nombre_Interventions=("Shift", "count"),
                Total_Carburant_Litres=("Litres_Carburant", "sum"),
                Montant_Total_Carburant=("Cout_Carburant", "sum"),
                Montant_Total_Location=("Cout_Location", "sum"),
                Montant_Total_Du=("Cout_Total", "sum")
            ).reset_index()
            st.dataframe(chargeuses_resume, use_container_width=True)
        else:
            st.info("Aucune chargeuse enregistrée.")
    else:
        st.info("Aucun bon de sortie enregistré.")

# --- ONGLET 4 : RAPPORT PAR SHIFT (AVEC EXPORT PDF) ---
with tab_rapport_shift:
    st.subheader("📊 Rapport Détaillé par Shift & Export PDF")
    
    c_rep_date, c_rep_shift = st.columns(2)
    with c_rep_date:
        sel_date = st.date_input("Date du rapport", value=datetime.today(), key="rep_date")
    with c_rep_shift:
        sel_shift = st.selectbox("Shift concerné", [SHIFT_JOUR, SHIFT_NUIT], key="rep_shift")

    if st.session_state.historique_bons:
        df_hist = pd.DataFrame(st.session_state.historique_bons)
        df_shift_filtered = df_hist[(df_hist["Date"] == str(sel_date)) & (df_hist["Shift"] == sel_shift)]
        
        st.markdown(f"##### Activités du {sel_date} - {sel_shift}")
        if not df_shift_filtered.empty:
            st.dataframe(df_shift_filtered, use_container_width=True)
            total_shift_cout = df_shift_filtered["Cout_Total"].sum()
            st.metric("Coût Total pour ce Shift", f"{total_shift_cout:,.0f} FCFA")
            
            pdf_buffer = generer_pdf_shift(str(sel_date), sel_shift, df_shift_filtered)
            st.download_button(
                label="📥 Télécharger le Rapport du Shift en PDF",
                data=pdf_buffer,
                file_name=f"Rapport_Shift_{sel_date}_{sel_shift.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        else:
            st.info("Aucune opération enregistrée pour ce shift précis.")
    else:
        st.info("Aucune donnée disponible.")

# --- ONGLET 5 : RAPPORT GLOBAL DES SHIFTS (AVEC EXPORT PDF) ---
with tab_rapport_global:
    st.subheader("📈 Rapport Global de Toutes les Opérations (CFDAI) & Export PDF")
    
    if st.session_state.historique_bons:
        df_g = pd.DataFrame(st.session_state.historique_bons)
        
        camions_g = df_g[df_g["Categorie"] == "Camion"]
        chargeuses_g = df_g[df_g["Categorie"] == "Chargeuse"]
        personnel_g = df_g[df_g["Categorie"] == "Personnel"]

        nb_camions_total = camions_g["Identifiant"].nunique() if not camions_g.empty else 0
        total_tours_glob = len(camions_g)
        total_carb_cam = camions_g["Cout_Carburant"].sum() if not camions_g.empty else 0
        total_loc_cam = camions_g["Cout_Location"].sum() if not camions_g.empty else 0

        total_carb_ch = chargeuses_g["Cout_Carburant"].sum() if not chargeuses_g.empty else 0
        total_loc_ch = chargeuses_g["Cout_Location"].sum() if not chargeuses_g.empty else 0

        total_mo_glob = personnel_g["Cout_Total"].sum() if not personnel_g.empty else 0

        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.metric("Nombre de Camions Engagés", f"{nb_camions_total} camions")
            st.metric("Total Tours Camions", f"{total_tours_glob} tours (bons)")
            st.metric("Coût Carburant Camions", f"{total_carb_cam:,.0f} FCFA")
            st.metric("Location Camions", f"{total_loc_cam:,.0f} FCFA")
        with col_g2:
            st.metric("Coût Carburant Chargeuses", f"{total_carb_ch:,.0f} FCFA")
            st.metric("Location Chargeuses", f"{total_loc_ch:,.0f} FCFA")
        with col_g3:
            st.metric("Total Main d'Œuvre Entretien", f"{total_mo_glob:,.0f} FCFA")

        st.markdown("---")
        st.markdown("### 🏆 Top 5 des Camions les Plus Actifs")
        if not camions_g.empty:
            top_5_camions = camions_g.groupby("Identifiant").agg(
                Type_Camion=("Type_Camion", "first"),
                Nombre_Tours=("Numero_Bon", "count"),
                Total_Litres=("Litres_Carburant", "sum"),
                Montant_Total_Du=("Cout_Total", "sum")
            ).reset_index().sort_values(by="Nombre_Tours", ascending=False).head(5)
            st.dataframe(top_5_camions, use_container_width=True)
        else:
            st.info("Aucun camion enregistré.")

        cout_total_global = total_carb_cam + total_loc_cam + total_carb_ch + total_loc_ch + total_mo_glob
        st.markdown("---")
        st.markdown(f"### 💰 Coût Total Global de l'Opération CFDAI : **{cout_total_global:,.0f} FCFA**")
        
        pdf_global_buffer = generer_pdf_global(df_g)
        st.download_button(
            label="📥 Télécharger le Rapport Global en PDF",
            data=pdf_global_buffer,
            file_name=f"Rapport_Global_CFDAI_{datetime.now().strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Aucune donnée globale disponible.")