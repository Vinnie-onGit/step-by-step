from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset
from utils.api_service import ApiService  # Servizio API per chiamare il backend

api_service = ApiService()

class ActionGenerateTapparellaQuote(Action):
    """Genera un preventivo per la tapparella"""

    def name(self) -> Text:
        return "action_generate_tapparella_quote"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        dimensione = tracker.get_slot("dimensione")
        materiale = tracker.get_slot("materiale")
        colore = tracker.get_slot("colore")
        accessori = tracker.get_slot("accessori") or []

        if not dimensione or not materiale or not colore:
            dispatcher.utter_message(text="⚠️ Mi servono le dimensioni, il materiale e il colore per calcolare il preventivo.")
            return []

        # Richiesta API per ottenere il preventivo
        response = api_service.post("configura_tapparella", {
            "materiale": materiale,
            "larghezza": int(dimensione.split("x")[0]),
            "altezza": int(dimensione.split("x")[1]),
            "colore": colore,
            "accessori": accessori
        })

        if "errore" in response:
            dispatcher.utter_message(text=f"⚠️ Errore: {response['errore']}")
            return []

        preventivo = response["preventivo"]
        messaggio = f"""
        🏠 Preventivo per la tua tapparella 🏠
        📏 Dimensioni: {preventivo['dimensioni']}
        🏗 Materiale: {materiale}
        🎨 Colore: {preventivo['colore']}
        🛠 Accessori: {", ".join(accessori) if accessori else "Nessuno"}
        
        💵 **Totale preventivo: {preventivo['prezzo_totale']:.2f}€** ✅
        """

        dispatcher.utter_message(text=messaggio)

        buttons = [
            {"title": "Sì, conferma", "payload": "/confirm_tapparella"},
            {"title": "Voglio cambiare opzioni", "payload": "/change_tapparella"},
        ]
        dispatcher.utter_message(text="Vuoi confermare questo preventivo o preferisci modificarlo?", buttons=buttons)

        return []

class ValidateTapparellaQuoteForm(FormValidationAction):
    """Valida il form per la configurazione della tapparella"""

    def name(self) -> Text:
        return "validate_tapparella_quote_form"

    async def validate_dimensione(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida la dimensione fornita dall'utente"""
        if "x" in slot_value:
            larghezza, altezza = slot_value.split("x")
            try:
                int(larghezza), int(altezza)
                return {"dimensione": slot_value}
            except ValueError:
                dispatcher.utter_message(text="⚠️ Usa il formato corretto per le dimensioni: larghezza x altezza (es. 120x100).")
                return {"dimensione": None}
        dispatcher.utter_message(text="⚠️ Puoi fornire le dimensioni nel formato corretto? (es. 120x100)")
        return {"dimensione": None}


    async def validate_colore(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Se l'utente ha fornito il colore, chiudiamo il form"""
        if slot_value:
            return {"colore": slot_value}
        dispatcher.utter_message(text="⚠️ Per favore, scegli un colore valido.")
        return {"colore": None}
