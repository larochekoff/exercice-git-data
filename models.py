"""
models.py - Structures de données métier sans agrégation trompeuse.
"""

from dataclasses import dataclass
from datetime import date, time
from typing import List

@dataclass
class BonSortieCamion:
    date_op: date
    shift: str
    heure_prise: time
    num_bon: str
    matricule: str
    type_camion: str
    prise_gazole: bool
    carburant_litres: float
    motif_ajustement: str
    nb_voyages: int = 1

    def clean_and_validate(self) -> List[str]:
        erreurs = []
        self.num_bon = self.num_bon.strip().upper() if self.num_bon else ""
        self.matricule = self.matricule.strip().upper().replace(" ", "") if self.matricule else ""

        if not self.num_bon:
            erreurs.append("Le N° de Bon de sortie est obligatoire.")
        if not self.matricule:
            erreurs.append("Le matricule du camion est obligatoire.")
        if self.prise_gazole and self.carburant_litres <= 0:
            erreurs.append("Veuillez indiquer le volume de gazole servi (> 0 L).")
        return erreurs


@dataclass
class ChargeuseEntry:
    date_op: date
    shift: str
    heure_prise: time
    id_chargeuse: str
    carburant_l: float
    motif_ajustement: str
    en_service_24h: bool

    def clean_and_validate(self) -> List[str]:
        erreurs = []
        self.id_chargeuse = self.id_chargeuse.strip().upper() if self.id_chargeuse else ""
        if not self.id_chargeuse:
            erreurs.append("L'identifiant de la chargeuse est obligatoire.")
        return erreurs


@dataclass
class PersonnelEntry:
    date_op: date
    shift: str
    equipe_active: bool
    effectif_present: int
    motif_absence: str