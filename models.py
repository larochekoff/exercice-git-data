"""
models.py: Structures de données et initialisation de l'état de session
"""
import streamlit as st
from config import (
    DEFAULT_TARIF_CARBURANT,
    DEFAULT_LOCATION_12_ROUES,
    DEFAULT_LOCATION_10_ROUES,
    DEFAULT_LOCATION_CHARGEUSES,
    DEFAULT_MAINS_OEUVRE_JOUR,
    DEFAULT_MAINS_OEUVRE_NUIT
)

def init_session_state():
    """Initialise les tables de données et les paramètres dans la session Streamlit."""
    if "tarifs" not in st.session_state:
        st.session_state.tarifs = {
            "carburant": DEFAULT_TARIF_CARBURANT,
            "loc_12_roues": DEFAULT_LOCATION_12_ROUES,
            "loc_10_roues": DEFAULT_LOCATION_10_ROUES,
            "loc_chargeuses": DEFAULT_LOCATION_CHARGEUSES,
            "mo_jour": DEFAULT_MAINS_OEUVRE_JOUR,
            "mo_nuit": DEFAULT_MAINS_OEUVRE_NUIT
        }

    if "saisies_camions" not in st.session_state:
        st.session_state.saisies_camions = []

    if "saisies_chargeuses" not in st.session_state:
        st.session_state.saisies_chargeuses = []

    if "saisies_personnel" not in st.session_state:
        st.session_state.saisies_personnel = []