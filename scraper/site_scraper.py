import requests
from bs4 import BeautifulSoup
import json

# URL della pagina da cui estrarre i dati
url = "https://www.letapparelle.com/tapparelle_avvolgibili_in_alluminio_coibentato_52.html"

# Effettua la richiesta HTTP
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Errore nel recuperare la pagina: {response.status_code}")
    
# Parsing del contenuto HTML
soup = BeautifulSoup(response.text, "html.parser")

# Trova tutti i div che contengono il tag span con il testo desiderato
color_divs = soup.find_all("div", class_="tap-color-container colore")

# Estrai il testo all'interno del tag <span> di ciascun div
color_values = []
for div in color_divs:
    span = div.find("span")
    if span:
        text = span.get_text(strip=True)
        if text:
            color_values.append(text)

# Genera un documento JSON con i valori estratti
output_document = {"color_values": color_values}

# Stampa il documento JSON formattato
print(json.dumps(output_document, indent=4, ensure_ascii=False))
