import json
import os

# Percorso file di input
INPUT_FILE = "dataset/motori_tapparelle.json"

# Cartella di output
OUTPUT_DIR = "dataset/prodotti_per_categoria"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_products():
    """Carica il file JSON contenente tutti i prodotti."""
    if not os.path.exists(INPUT_FILE):
        print("[ERROR] File JSON non trovato!")
        return []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def categorize_products(products):
    """Divide i prodotti in base alla loro categoria."""
    categories = {}

    for product in products:
        title = product.get("title", "").lower()

        # Determina la categoria basandosi sul titolo
        if "motore" in title:
            category = "motori"
        elif "telecomando" in title or "radiocomando" in title:
            category = "telecomandi"
        elif "pulsante" in title or "interruttore" in title:
            category = "pulsanti"
        elif "accessorio" in title or "kit" in title:
            category = "accessori"
        else:
            category = "altri"

        if category not in categories:
            categories[category] = []

        categories[category].append(product)

    return categories

def save_categories(categories):
    """Salva ogni categoria in un file JSON separato."""
    for category, items in categories.items():
        output_path = os.path.join(OUTPUT_DIR, f"{category}.json")
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(items, file, indent=4, ensure_ascii=False)
        print(f"[SUCCESS] Salvato {len(items)} prodotti in {output_path}")

def main():
    """Esegue la divisione dei prodotti per categoria."""
    print("[INFO] Caricamento prodotti...")
    products = load_products()

    if not products:
        print("[ERROR] Nessun prodotto trovato.")
        return

    print("[INFO] Classificazione prodotti...")
    categorized_products = categorize_products(products)

    print("[INFO] Salvataggio categorie...")
    save_categories(categorized_products)

    print("[DONE] Suddivisione completata!")

if __name__ == "__main__":
    main()
