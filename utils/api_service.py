import requests
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional


# Sceglie il .env corretto
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env.dev")
# Carica le variabili d'ambiente
load_dotenv(dotenv_path=dotenv_path)

# Configurazione logging
logger = logging.getLogger("ApiService")

print(f"API BASE URL: {os.getenv('API_URL')}")

javaBaseUrl = "http://localhost:8080/api/v1"
varianteEndpoint = "varianti"
varianteInfoEndpoint = "varianteInfo"
tapparelleEndpoint = "tapparelle"
prodottiEndpoint = "prodotti"


class ApiService:
    """Classe per gestire le richieste all'API dei prodotti."""

    def __init__(self):
        """Inizializza il servizio API con l'URL base."""
        self.base_url = os.getenv("API_URL")  # Assicurati che API_URL sia nel file .env
        self.javaBaseUrl = javaBaseUrl
        self.varianteUrl = varianteEndpoint
        self.varianteInfoUrl = varianteInfoEndpoint
        self.tapparelleUrl = tapparelleEndpoint
        self.prodottiUrl = prodottiEndpoint

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        """Effettua una richiesta GET all'API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore nella richiesta GET a {url}: {e}")
            return None

    def post(self, endpoint: str, data: Dict[str, Any]):
        """Effettua una richiesta POST all'API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            logger.info(
                f"La chiamata post è stata eseguita all'endpoint {self.base_url}/{endpoint}"
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Errore nella richiesta POST a {url}: {e}")
            return None

    def get_motori(self, potenza_min: int):
        """Recupera i motori dalla API in base alla potenza minima"""
        response = requests.get(
            f"{self.base_url}/motori", params={"potenza_min": potenza_min}
        )
        return response.json().get("prodotti", [])

    def get_colori(self, materiale: str):
        if materiale == "alluminio coibentato":
            response = requests.get(
                f"{self.base_url}/colori_tapparelle", params=materiale
            )
            return response.json().get("colori", [])
        if materiale == "pvc":
            response = requests.get(
                f"{self.base_url}/colori_tapparelle", params=materiale
            )
            return response.json().get("colori", [])

    def get_colore(self, materiale: str, colore: str):
        lista_colori = []
        colori = []
        if materiale == "alluminio coibentato":
            lista_colori = self.get_colori("alluminio")
        elif materiale == "pvc":
            lista_colori = self.get_colori(materiale)

        for colore in lista_colori:
            if colore in lista_colori:
                colori.append(colori)
        return colori

    def get_tapparelle(self):
        tapparelle = []
        try:
            tapparelle = requests.get(f"{self.javaBaseUrl}/{prodottiEndpoint}/")
            tapparelle.raise_for_status()
            print(tapparelle)
            return tapparelle.json()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Errore nella richiesta get a {self.javaBaseUrl}/{prodottiEndpoint}/"
            )
            return {"error": str(e)}
