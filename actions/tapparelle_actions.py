import logging
from typing import Any, Dict, List, Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

from utils.api_service import ApiService  # Servizio API per chiamare il backend

logger = logging.getLogger("TapparelleLog")
api_service = ApiService()


class ActionGenerateTapparellaQuote(Action):
    """Chiamata all'endpoint /configura_tapparella per generare il preventivo."""

    def name(self) -> Text:
        return "action_generate_tapparella_quote"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dimensioni = tracker.get_slot("dimensioni")
        materiale = tracker.get_slot("materiale")
        colore = tracker.get_slot("colore")

        if not dimensioni or not materiale or not colore:
            dispatcher.utter_message(
                text="⚠️ Mi servono le dimensioni, il materiale e il colore per calcolare il preventivo."
            )
            return []

        payload = {"dimensioni": dimensioni, "materiale": materiale, "colore": colore}
        logger.debug(f"Invio richiesta a /configura_tapparella con payload: {payload}")
        response = api_service.post("configura_tapparella", payload)
        logger.debug(f"Risposta da /configura_tapparella: {response}")

        if "preventivo" in response:
            preventivo = response["preventivo"]
            messaggio = f"""
🏠 Preventivo per la tua tapparella 🏠
📏 Dimensioni: {preventivo.get("dimensioni")}
🏗 Materiale: {materiale.upper()}
🎨 Colore: {preventivo.get("colore")}
💵 Totale preventivo: {preventivo.get("prezzo_totale"):.2f}€ ✅
"""
            dispatcher.utter_message(text=messaggio)
        else:
            dispatcher.utter_message(text="⚠️ Errore nella generazione del preventivo.")

        return []


class ActionAskColoreTapparella(Action):
    """Chiede all'utente di scegliere il colore tra quelli disponibili per il materiale specificato."""

    def name(self) -> Text:
        return "action_ask_colore_tapparella"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Any, Text],
    ) -> List[Dict[Text, Any]]:
        materiale = tracker.get_slot("materiale")
        if not materiale:
            dispatcher.utter_message(
                "Non hai specificato il materiale della tapparella."
            )
            return []

        materiale_lower = materiale.strip().lower()
        response = api_service.get(
            "colori_tapparelle", params={"materiale": materiale_lower}
        )
        if not response or "data" not in response:
            dispatcher.utter_message(text="Errore nel recupero dei colori.")
            return []

        colori_disponibili = response["data"]
        message = (
            f"I colori disponibili per le tapparelle in {materiale.upper()} sono:\n"
        )
        for colore_doc in colori_disponibili:
            color_value = colore_doc.get("color", "N/D")
            message += f"• {color_value}\n"
        message += "\nScegli pure il colore che preferisci!"
        dispatcher.utter_message(text=message)
        return []


class ValidateTapparellaQuoteForm(FormValidationAction):
    """
    Action di validazione per il form di configurazione della tapparella.
    Verifica i valori inseriti per ciascun slot.
    """

    def name(self) -> Text:
        return "validate_tapparella_quote_form"

    async def validate_dimensioni(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if "x" in slot_value:
            return {"dimensioni": slot_value}
        else:
            dispatcher.utter_message(
                text="Inserisci le dimensioni nel formato '120x100'."
            )
            return {"dimensioni": None}

    async def validate_materiale(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        materiale_input = str(slot_value).strip().lower()
        valid_materials = ["pvc", "alluminio coibentato"]
        if materiale_input in valid_materials:
            return {"materiale": materiale_input}
        else:
            dispatcher.utter_message(
                text="Il materiale inserito non è valido. Scegli tra 'PVC' o 'alluminio coibentato'."
            )
            return {"materiale": None}

    async def validate_colore(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value and slot_value.strip():
            return {"colore": slot_value.strip()}
        dispatcher.utter_message(text="Inserisci un colore valido.")
        return {"colore": None}


class ActionGeneratePreventivo(Action):
    def name(self):
        return "action_generate_preventivo"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dimensioni = tracker.get_slot("dimensioni")
        materiale = tracker.get_slot("materiale")
        colore = tracker.get_slot("colore")

        dispatcher.utter_message(
            text=f"""
            Dimensioni: {dimensioni}\n
            Materiale: {materiale}\n
            Colore: {colore}\n
            """
        )
        return []


class ActionListTapparelle(Action):
    def name(self):
        return "action_list_tapparelle"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        tapparelle = []
        tapparelle = api_service.get_tapparelle()
        print(tapparelle)
        message = ""
        for tapparella in tapparelle:
            message += f"ID:{tapparella.get('idProdotto')}\tNOME: {tapparella.get('nomeProdotto')}\tPREZZO:{tapparella.get('prezzoProdotto')} euro\n"
        dispatcher.utter_message(text=message)
        return []
