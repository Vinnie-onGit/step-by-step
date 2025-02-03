from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset 
from utils.api_service import ApiService  # Servizio API per recuperare i motori

api_service = ApiService()

class ActionGenerateMotorQuote(Action):
    """Genera un preventivo per il motore della tapparella"""

    def name(self) -> Text:
        return "action_generate_motor_quote"

    def calcola_peso_tapparella(self, dimensione: str, materiale: str) -> float:
        """Calcola il peso della tapparella in base alle dimensioni e al materiale"""
        larghezza, altezza = map(int, dimensione.split("x"))

        pesi_materiali = {
            "alluminio": 4.5,
            "pvc": 3.0,
            "acciaio": 7.0,
            "PVC leggero" : 4.0,
            "PVC rinforzato" : 5.0 ,
            "Alluminio coibentato" : 5.5,
            "Alluminio estruso" : 7.0,
            "Acciaio blindato" : 8.5,
        }

        peso_m2 = pesi_materiali.get(materiale.lower(), 4.0)
        peso_totale = (larghezza / 100) * (altezza / 100) * peso_m2
        return round(peso_totale, 2)

    def trova_potenza_minima(self, peso: float) -> int:
        """Trova la potenza minima richiesta per il motore in base al peso della tapparella"""
        if peso > 80:
            return 50
        elif peso > 60:
            return 40
        elif peso > 40:
            return 30
        else:
            return 20

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        dimensione = tracker.get_slot("dimensione")
        materiale = tracker.get_slot("materiale")

        if not dimensione or not materiale:
            dispatcher.utter_message(text="⚠️ Mi servono le dimensioni e il materiale della tapparella per calcolare il preventivo.")
            return []

        peso_tapparella = self.calcola_peso_tapparella(dimensione, materiale)
        peso_per_motore = self.trova_potenza_minima (peso_tapparella)
        motori = api_service.get_motori(peso_per_motore)

        if not motori:
            dispatcher.utter_message(text="⚠️ Non ho trovato un motore adatto per questa tapparella.")
            return []

        # Prende il motore più economico
        motore_selezionato = sorted(motori, key=lambda x: float(x["prezzo_prodotto"]))[0]
        prezzo_totale = float(motore_selezionato["prezzo_prodotto"])

        preventivo = f"""
        🔧 Preventivo per il Motore 🔧
        📏 Dimensioni: {dimensione}
        🏗 Materiale: {materiale}
        ⚖️ Peso stimato: {peso_tapparella} kg
        ⚙️ Motore: {motore_selezionato['nome_prodotto']} - 💰 {prezzo_totale}€
        """

        dispatcher.utter_message(text=preventivo)

        # Offriamo **alternative**
        buttons = [
            {"title": "Sì, conferma", "payload": "/confirm_motor"},
            {"title": "Voglio vedere altre opzioni", "payload": "/change_motor"},
        ]
        dispatcher.utter_message(text="Vuoi confermare questo motore o preferisci vederne altri?", buttons=buttons)

        return []

class ValidateMotorQuoteForm(FormValidationAction):
    """Classe per validare il form `motor_quote_form`"""

    def name(self) -> Text:
        return "validate_motor_quote_form"

    async def validate_dimensione(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida la dimensione fornita dall'utente"""
        if "x" in slot_value:
            larghezza, altezza = slot_value.split("x")
            try:
                larghezza = int(larghezza)
                altezza = int(altezza)
                return {"dimensione": slot_value}
            except ValueError:
                dispatcher.utter_message(text="⚠️ Il formato delle dimensioni non è corretto. Usa il formato: larghezza x altezza (es. 120x100).")
                return {"dimensione": None}
        dispatcher.utter_message(text="⚠️ Non ho capito le dimensioni. Puoi fornirle nel formato corretto? (es. 120x100)")
        return {"dimensione": None}

    async def validate_materiale(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Valida il materiale fornito dall'utente"""
        
        materiali_validi = ["alluminio", "pvc", "acciaio", "alluminio coibentato", "acciaio blindato"]
        
                # Verifica se l'utente sta cercando di avviare un preventivo invece di fornire il materiale
        intent_utente = tracker.latest_message.get("intent", {}).get("name", "")

        if intent_utente == "generate_motor_quote":
            dispatcher.utter_message(text="Devo prima conoscere le dimensioni e il materiale della tapparella.")
            return {"materiale": None}
        
        if slot_value.lower() not in materiali_validi:
            dispatcher.utter_message(
                text=f"❌ Il materiale '{slot_value}' non è valido. Scegli tra: {', '.join(materiali_validi)}"
            )
            return {"materiale": None}  # Reset dello slot per ripetere la richiesta

        return {"materiale": slot_value.lower()}

    async def validate_motore(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Se l'utente ha già scelto un motore, lo conferma. Altrimenti, suggerisce il migliore."""
        dimensione = tracker.get_slot("dimensione")
        if slot_value:
            return {"motore": slot_value}
        
        if dimensione:
            larghezza, altezza = map(int, dimensione.split("x"))
            peso_tapparella = larghezza * altezza * 0.005  # Calcolo del peso stimato

            # Ricerca il motore adatto
            motori = api_service.get("motori")
            if motori:
                for motore in motori:
                    potenza = motore.get("potenza_nm", 0)
                    if potenza >= peso_tapparella:
                        dispatcher.utter_message(text=f"📌 Ti consiglio il motore {motore['nome_prodotto']} con {potenza}Nm di potenza.")
                        return {"motore": motore['nome_prodotto']}

        dispatcher.utter_message(text="⚠️ Non ho trovato un motore adatto. Puoi specificare una preferenza?")
        return {"motore": None}
    
class ActionConfirmMotor(Action):
    def name(self) -> Text:
        return "action_confirm_motor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        dimensione = tracker.get_slot("dimensione")
        materiale = tracker.get_slot("materiale")
        motore = tracker.get_slot("motore")

        conferma = f"""
        ✅ Conferma del Preventivo ✅
        📏 Dimensioni: {dimensione}
        🏗  Materiale: {materiale}
        ⚙️ Motore scelto: {motore}
        """

        dispatcher.utter_message(text=conferma)
        dispatcher.utter_message(text="Grazie per la richiesta! Ti contatteremo presto.")

        # 🔄 Reset degli slot dopo la conferma
        return [AllSlotsReset()]

class ActionFinalizeMotor(Action):
    """Conferma il motore selezionato e termina il flusso di preventivo"""

    def name(self):
        return "action_finalize_motor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        motore = tracker.get_slot("motore")

        if motore:
            dispatcher.utter_message(f"✅ Il motore **{motore['nome_prodotto']}** è stato confermato! Procediamo con l'ordine. 🚀")
            return [SlotSet("motore", None)]  # Reset dello slot
        else:
            dispatcher.utter_message("❌ Nessun motore selezionato. Vuoi vederne altri?")
            return []


class ActionResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("dimensione", None), SlotSet("materiale", None), SlotSet("motore", None)]
