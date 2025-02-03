import logging
import os
from config.settings import settings

#crea cartella logs se non esiste
os.makedirs (os.path.dirname (settings.LOG_FILE), exist_ok=True)

# Configurazione base del logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE, mode="a"),
        logging.StreamHandler()  # Mostra i log anche in console
    ]
)

logger =  logging.getLogger("RasaBot")
