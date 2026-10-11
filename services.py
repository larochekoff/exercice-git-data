"""
services.py: Logique métier, calculs et gestion des règles (carburant, location, rapports)
"""
import pandas as pd

class BusinessLogic:
    @staticmethod
    def calculer_carburant(litres, prix_litre):
        return litres * prix_litre

    @staticmethod
    def verifier_et_appliquer_location_camion(historique_camion, camion_id, shift_actuel):
        """
        Vérifie si la location doit être facturée (1 fois tous les 2 shifts, en comptant à partir du 1er shift).
        """
        camion_entries = [e for e in historique_camion if e.get("identifiant") == camion_id]
        nb_shifts_passes = len(camion_entries)
        facturer = (nb_shifts_passes % 2 == 0)
        return facturer

    @staticmethod
    def verifier_et_appliquer_location_chargeuse(historique_chargeuse, chargeuse_id):
        """
        Règle similaire pour les chargeuses (location tous les 2 shifts).
        """
        chargeuse_entries = [e for e in historique_chargeuse if e.get("identifiant") == chargeuse_id]
        nb_shifts_passes = len(chargeuse_entries)
        facturer = (nb_shifts_passes % 2 == 0)
        return facturer

    @staticmethod
    def generer_rapport_journalier(date_selectionnee, camions, chargeuses, personnel):
        """Génère un dictionnaire de DataFrames consolidés pour une date spécifique."""
        df_c = pd.DataFrame(camions)
        df_ch = pd.DataFrame(chargeuses)
        df_p = pd.DataFrame(personnel)

        res = {}
        if not df_c.empty and "Date" in df_c.columns:
            res["camions"] = df_c[df_c["Date"] == str(date_selectionnee)]
        else:
            res["camions"] = pd.DataFrame()

        if not df_ch.empty and "Date" in df_ch.columns:
            res["chargeuses"] = df_ch[df_ch["Date"] == str(date_selectionnee)]
        else:
            res["chargeuses"] = pd.DataFrame()

        if not df_p.empty and "Date" in df_p.columns:
            res["personnel"] = df_p[df_p["Date"] == str(date_selectionnee)]
        else:
            res["personnel"] = pd.DataFrame()

        return res

    @staticmethod
    def generer_rapport_global(camions, chargeuses, personnel):
        """Consolide l'ensemble des opérations de tous les jours."""
        return {
            "camions": pd.DataFrame(camions),
            "chargeuses": pd.DataFrame(chargeuses),
            "personnel": pd.DataFrame(personnel)
        }