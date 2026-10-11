"""
config.py - Paramètres globaux, grille tarifaire et identification.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class BusinessConfig:
    NOM_STRUCTURE: str = "--- Embarquement Navire CFDAI ---"

    DEFAULT_PRIX_CARBURANT_LITRE: float = 715.0
    DEFAULT_TARIF_10_ROUES_24H: float = 150000.0
    DEFAULT_TARIF_12_ROUES_24H: float = 200000.0
    DEFAULT_TARIF_CHARGEUSE_24H: float = 280000.0
    DEFAULT_TARIF_PERS_JOUR: float = 50000.0
    DEFAULT_TARIF_PERS_NUIT: float = 60000.0

    SHIFT_JOUR_LABEL: str = "Jour (08h00 ➔ 19h00)"
    SHIFT_NUIT_LABEL: str = "Nuit (19h00 ➔ 08h00 J+1)"

    CODE_SECRET_RESET: str = "RESET-CAJOU"

CONFIG = BusinessConfig()