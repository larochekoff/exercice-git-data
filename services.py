"""
services.py - Calculs financiers basés sur les bons individuels et générateur PDF.
"""

import pandas as pd
import io
from datetime import date
from typing import Dict, Any, List
from config import CONFIG

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class BusinessEngine:

    @staticmethod
    def calculate_daily_financials(df_camions_day: pd.DataFrame, df_ch_day: pd.DataFrame, 
                                  df_p_day: pd.DataFrame, rates: Dict[str, float]) -> Dict[str, Any]:
        
        # Rotations = Nombre exact de bons enregistrés
        tot_voyages = len(df_camions_day) if not df_camions_day.empty else 0
        
        if not df_camions_day.empty:
            # Facturation location : 1 seul forfait 24h par véhicule distinct (matricule)
            df_cam_unique = df_camions_day.drop_duplicates(subset=["Matricule"])
            loc_camions = df_cam_unique["Type Camion"].apply(
                lambda x: rates["10_roues"] if "10" in str(x) else rates["12_roues"]
            ).sum()
            # Carburant = Somme réelle des litres servis sur chaque bon
            carb_camions_L = df_camions_day["Carburant (L)"].sum()
        else:
            loc_camions, carb_camions_L = 0.0, 0.0

        if not df_ch_day.empty:
            df_ch_unique = df_ch_day.drop_duplicates(subset=["ID Chargeuse"])
            loc_chargeuses = (df_ch_unique["En Service (24h)"].sum()) * rates["chargeuse"]
            carb_ch_L = df_ch_day["Carburant (L)"].sum()
        else:
            loc_chargeuses, carb_ch_L = 0.0, 0.0

        cost_personnel = 0.0
        if not df_p_day.empty:
            for _, p_row in df_p_day.iterrows():
                if p_row.get("Equipe Active", False):
                    cost_personnel += rates["pers_jour"] if "Jour" in str(p_row.get("Shift", "")) else rates["pers_nuit"]

        total_carb_L = carb_camions_L + carb_ch_L
        cost_carb_total = round(total_carb_L * rates["carburant"])
        grand_total = round(loc_camions + loc_chargeuses + cost_carb_total + cost_personnel)

        return {
            "tot_voyages": int(tot_voyages),
            "loc_camions": round(loc_camions),
            "loc_chargeuses": round(loc_chargeuses),
            "carb_camions_L": round(carb_camions_L, 1),
            "total_carb_L": round(total_carb_L, 1),
            "cost_carb_total": cost_carb_total,
            "cost_personnel": round(cost_personnel),
            "grand_total": grand_total
        }

    @staticmethod
    def reset_all_data(session_state) -> None:
        session_state.historique_camions = pd.DataFrame()
        session_state.historique_chargeuses = pd.DataFrame()
        session_state.historique_personnel = pd.DataFrame()


class ReportPDFGenerator:

    @staticmethod
    def generate_daily_pdf(date_op: date, financials: Dict[str, Any], rates: Dict[str, float]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
        story = []
        styles = getSampleStyleSheet()

        company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor("#1A365D"), fontName='Helvetica-Bold')
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=13, textColor=colors.HexColor("#2B6CB0"), spaceAfter=6)
        body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8.5, leading=11)

        story.append(Paragraph(f"<b>{CONFIG.NOM_STRUCTURE}</b>", company_style))
        story.append(Paragraph("<b>FICHE DE RAPPORT JOURNALIER D'EMBARQUEMENT</b>", title_style))
        story.append(Paragraph(f"<b>Date d'opération :</b> {date_op.strftime('%d/%m/%Y')}", body))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceBefore=6, spaceAfter=8))

        data_kpi = [
            ["Poste de Dépense", "Valeur / Quantité"],
            ["Total Rotations", f"{financials['tot_voyages']} tours"],
            ["Location Camions Bennes", f"{financials['loc_camions']:,.0f} FCFA"],
            ["Location Chargeuses", f"{financials['loc_chargeuses']:,.0f} FCFA"],
            ["Gazole Consommé", f"{financials['total_carb_L']:,} Litres ({financials['cost_carb_total']:,.0f} FCFA)"],
            ["Personnel d'Entretien", f"{financials['cost_personnel']:,.0f} FCFA"],
            ["DÉPENSE TOTALE JOUR", f"{financials['grand_total']:,.0f} FCFA"]
        ]
        t_kpi = Table(data_kpi, colWidths=[260, 240])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FEFCBF")),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        story.append(t_kpi)

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_global_pdf(df_all_cam: pd.DataFrame, df_all_ch: pd.DataFrame, 
                            df_all_p: pd.DataFrame, rates: Dict[str, float]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
        story = []
        styles = getSampleStyleSheet()

        company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor("#1A365D"), fontName='Helvetica-Bold')
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=13, textColor=colors.HexColor("#2B6CB0"), spaceAfter=6)

        story.append(Paragraph(f"<b>{CONFIG.NOM_STRUCTURE}</b>", company_style))
        story.append(Paragraph("<b>BILAN GLOBAL D'EMBARQUEMENT NAVIRE</b>", title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceBefore=6, spaceAfter=8))

        tot_tours = len(df_all_cam) if not df_all_cam.empty else 0
        tot_carb = (df_all_cam["Carburant (L)"].sum() if not df_all_cam.empty else 0) + (df_all_ch["Carburant (L)"].sum() if not df_all_ch.empty else 0)

        data_glob = [
            ["Indicateur Global", "Quantité Total"],
            ["Total Rotations Camions", f"{tot_tours} voyages"],
            ["Total Gazole Consommé", f"{tot_carb:,} Litres"]
        ]
        t_glob = Table(data_glob, colWidths=[250, 250])
        t_glob.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        story.append(t_glob)

        doc.build(story)
        buffer.seek(0)
        return buffer 