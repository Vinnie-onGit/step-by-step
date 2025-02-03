import re
from typing import Optional

# Densità media dei materiali in kg/m²
DENSITA_MATERIALI = {
    "PVC": 4.0,
    "PVC Rinforzato": 5.0,
    "Alluminio Coibentato": 5.5,
    "Alluminio Estruso": 7.0,
    "Acciaio Blindato": 8.5
}

class Calculations:
    """Classe per il calcolo del peso della tapparella in base alle dimensioni e al materiale."""

    @staticmethod
    def extract_dimensions(dimensione: str) -> Optional[tuple]:
        """Estrae larghezza e altezza in metri dalla stringa dimensionale es. '120x150 cm'."""
        match = re.search(r"(\d{2,3})x(\d{2,3})", dimensione)
        if match:
            larghezza = float(match.group(1)) / 100  # Conversione cm → m
            altezza = float(match.group(2)) / 100    # Conversione cm → m
            return larghezza, altezza
        return None, None

    @staticmethod
    def estimate_weight(dimensione: str, materiale: str = "PVC") -> Optional[float]:
        """Stima il peso della tapparella in base alle dimensioni e al materiale."""
        larghezza, altezza = Calculations.extract_dimensions(dimensione)
        if not larghezza or not altezza:
            return None

        # Ottieni la densità del materiale, usa PVC come default se non specificato
        densita = DENSITA_MATERIALI.get(materiale, 4.0)

        # Calcolo peso = larghezza * altezza * densità
        peso = larghezza * altezza * densita

        return round(peso, 2)  # Restituisce il peso arrotondato a 2 decimali
