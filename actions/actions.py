from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from utils.api_service import ApiService  # Importiamo il servizio API

api_service = ApiService()

class ActionGeneratePreventivo(Action):
    """Genera un preventivo basato sulle preferenze dell'utente e i prodotti disponibili"""

    def name(self) -> Text:
        return "action_generate_preventivo"

    def trova_motore_adatto(self, dimensione: str) -> Dict[str, Any]:
        """Seleziona il motore più adatto in base alla dimensione della tapparella"""
        
        larghezza, altezza = map(int, dimensione.split("x"))
        peso_tapparella = (larghezza * altezza * 0.005)  # Peso stimato in kg per cm²

        # Recupera i motori disponibili dall'API con filtro sulla potenza minima
        motori = api_service.get("prodotti", params={"categoria": "motori", "potenza_min": peso_tapparella})
        
        if not motori:
            return None

        return sorted(motori, key=lambda x: float(x["prezzo_prodotto"]))[0]  # Restituisce il motore più economico

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        dimensione = tracker.get_slot("dimensione")
        materiale = tracker.get_slot("materiale")
        colore = tracker.get_slot("colore")
        print (colore) # debug
        manovra = tracker.get_slot("manovra")
        motore_selezionato = tracker.get_slot("motore")
        pulsante = tracker.get_slot("pulsante")
        accessori = tracker.get_slot("accessori") or []

        # Se l'utente non ha scelto un motore, selezioniamo quello più adatto
        if not motore_selezionato:
            motore_selezionato = self.trova_motore_adatto(dimensione)

        if not motore_selezionato:
            dispatcher.utter_message(text="⚠️ Non ho trovato un motore adatto per questa tapparella.")
            return []

        prezzo_totale = float(motore_selezionato["prezzo_prodotto"])

        # Recupera il pulsante se richiesto
        if pulsante:
            pulsante_prodotto = api_service.get("prodotti", params={"categoria": "pulsanti", "nome_prodotto": pulsante})
            if pulsante_prodotto:
                prezzo_totale += float(pulsante_prodotto[0]["prezzo_prodotto"])

        # Recupera gli accessori se richiesti
        accessori_selezionati = []
        for accessorio in accessori:
            accessorio_prodotto = api_service.get("prodotti", params={"categoria": "accessori", "nome_prodotto": accessorio})
            if accessorio_prodotto:
                accessori_selezionati.append(accessorio_prodotto[0])
                prezzo_totale += float(accessorio_prodotto[0]["prezzo_prodotto"])

        # Creazione del preventivo finale
        preventivo = f"""
        🏠 Preventivo per la tua tapparella 🏠
        📏 Dimensioni: {dimensione}
        🏗 Materiale: {materiale}
        🎨 Colore: {colore}
        ⚙️ Manovra: {manovra}
        🏎 Motore: {motore_selezionato['nome_prodotto']} - 💰 {motore_selezionato['prezzo_prodotto']}€
        🔘 Pulsante: {pulsante or "Nessuno"}
        🛠 Accessori: {", ".join(a['nome_prodotto'] for a in accessori_selezionati) if accessori_selezionati else "Nessuno"}
        
        💵 **Totale preventivo: {prezzo_totale:.2f}€** ✅
        """

        dispatcher.utter_message(text=preventivo)
        return []

class ValidatePreventivoTapparellaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_preventivo_tapparella_form"

    async def validate_motore(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida il valore del motore: deve essere solo il nome del motore, non un'intera frase"""

        motori_validi = ["Somfy", "Nice", "Rollmatik", "Bubendorff"]  # Lista motori disponibili

        # Se il valore del motore è una frase lunga, estrai solo parole chiave
        parole = slot_value.split()  # Divide la frase in parole
        for parola in parole:
            if parola.capitalize() in motori_validi:
                return {"motore": parola.capitalize()}  # Restituisci solo il nome del motore
        
        dispatcher.utter_message(text="⚠️ Non ho capito quale motore vuoi. Puoi specificare uno tra Somfy, Nice, Rollmatik o Bubendorff?")
        return {"motore": None}

    async def validate_materiale(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida che il valore del motore sia valido prima di accettarlo"""

        if slot_value:
            dispatcher.utter_message(text=f"✅ È stato selezionato: {slot_value}")
            return {"materiale": slot_value}
        
        dispatcher.utter_message(text="Non ho capito la scelta del motore, puoi ripetere?")
        return {"materiale": None}

    async def validate_colore(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida il colore e imposta lo slot"""
        print(f"[DEBUG COLORE]{slot_value}") #debug
        if slot_value:
            return {"colore": slot_value}

        dispatcher.utter_message(text="Non ho capito il colore, puoi ripetere?")
        return {"colore": None}

    async def validate_dimensione(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida che il valore del motore sia valido prima di accettarlo"""

        if slot_value:
            dispatcher.utter_message(text=f"✅ È stato selezionato: {slot_value}")
            return {"dimensione": slot_value}
        
        dispatcher.utter_message(text="Non ho capito la scelta della dimensione, puoi ripetere?")
        return {"dimensione": None}
    
    async def validate_pulsante(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida che il valore del motore sia valido prima di accettarlo"""

        if slot_value:
            dispatcher.utter_message(text=f"✅ È stato selezionato: {slot_value}")
            return {"pulsante": slot_value}
        
        dispatcher.utter_message(text="Non ho capito la scelta del pulsante, puoi ripetere?")
        return {"pulsante": None}
    
 