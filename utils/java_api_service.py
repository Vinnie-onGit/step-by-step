import requests
import logging
from typing import Dict, Any, Optional


logger = logging.getLogger("Java Logger")
baseUrl = "/api/v1/"
varianteUrl = "varianti"
varianteInfoUrl = "varianteInfo"
tapparelleUrl = "tapparelle"
prodottiUrl = "prodotti"


class JavaApiService:
    """Classe che gestisce le api in spring boot"""

    def __init__(self):
        """Instanzia la classe che gestisce le richieste"""
        self.baseUrl = baseUrl
        self.varianteUrl = varianteUrl
        self.varianteInfoUrl = varianteInfoUrl
        self.tapparelleUrl = tapparelleUrl
        self.prodottiUrl = prodottiUrl

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        url = f"{prodottiUrl}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Errore nella chiamata get all'endpoint spring: {e}")
            return None
