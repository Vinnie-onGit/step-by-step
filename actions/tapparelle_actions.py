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

    # async def validate_materiale (
    #     slef, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict [Text, Any]
    # ) -> Dict[Text, Any]:
    #     """Valida il materiale fornito dall'utente"""
        
        
    async def validate_colore(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        colore = str(slot_value).strip().lower() if slot_value else ""
        if not colore:
            dispatcher.utter_message(text="⚠️ Per favore, inserisci un colore valido.")
            return {"colore": None}
        
        # Interroga la collezione varianti per verificare i colori ammessi
        response = api_service.get("varianti", params={"categoria": "tapparella"})
        if "data" in response:
            colori_ammessi = [doc.get("name", "").strip().lower() for doc in response["data"]]
            if colore in colori_ammessi:
                return {"colore": colore}
            else:
                dispatcher.utter_message(
                    text="⚠️ Il colore inserito non è valido. I colori ammessi sono: " + ", ".join(colori_ammessi)
                )
                return {"colore": None}
        else:
            dispatcher.utter_message(text="⚠️ Errore nel recupero dei colori ammessi. Riprova più tardi.")
            return {"colore": None}
        
        
class ActionAskColoreTapparella (Action) :
    
    def name (self):
        return "action_ask_colore_tapparella"
    
    def run (self, 
             dispatcher: CollectingDispatcher, 
             tracker: Tracker, 
             domain: Dict[Any, Text]
            )->List[Dict[Text, Any]]:
                
        materiale = tracker.get_slot ("materiale")
        if not materiale:
            dispatcher.utter_message ("Non hai specificato il materiale della tapparella.")
            return []
        
        materiale_lower = materiale.strip().lower()
        
        response = api_service.get ("colori_tapparelle", params = {"materiale": materiale_lower})
        
        colori_disponibili = response["data"]
        
        if not response or "data" not in response:
            dispatcher.utter_message (text="Errore nel recupero dei colori")
        
        message = f"I colori disponibili per le tapparelle in {materiale} sono:\n"
        for colore_doc in colori_disponibili:
            valore_colore += colore_doc.get["color", "N\D"]
            message += f"• {valore_colore}\n"
        message+= "\n Scegli pure il colore che preferisci!"
        
        dispatcher.utter_message (text=message)
        return []