import json
import re
from openai import OpenAI
from config import (
    HF_TOKEN, BASE_URL, MODEL_NAME, MAX_TOKENS, TEMPERATURE, TOP_P, ASK_QUESTION_TEMPLATE
)
import database as db
import predictor
from utils import get_prediction_interpretation

AQ10_QUESTIONS = [
    "Je remarque souvent les bruits faibles que les autres ne perçoivent pas.",
    "Je préfère faire les choses toujours de la même manière.",
    "Quand je lis une histoire, j'ai du mal à comprendre les intentions des personnages.",
    "Je suis souvent très concentré sur une seule partie d'un objet.",
    "Je remarque souvent les petits détails que les autres ne voient pas.",
    "J'ai du mal à comprendre pourquoi certaines choses blessent les autres.",
    "Je préfère parler aux autres plutôt que de les écouter.",
    "J'ai du mal à imaginer ce que ce serait d'être quelqu'un d'autre.",
    "Je trouve que les routines et les horaires sont rassurants pour moi.",
    "J'ai du mal à savoir comment me comporter dans différentes situations sociales."
]

DEMOGRAPHIC_QUESTIONS = [
    ("age",            "Quel est votre âge ? (ex: 21)"),
    ("gender",         "Quel est votre sexe ? (homme / femme / autre)"),
    ("ethnicity",      "Quelle est votre origine ethnique ?"),
    ("jaundice",       "Avez-vous eu la jaunisse à la naissance ? (oui / non)"),
    ("austim",         "Y a-t-il des antécédents familiaux d'autisme ? (oui / non)"),
    ("contry_of_res",  "Dans quel pays résidez-vous ?"),
    ("used_app_before","Avez-vous déjà utilisé une application similaire ? (oui / non)"),
    ("relation",       "Quel est votre lien avec la personne évaluée ? (moi-même / parent / proche / autre)"),
]

SYSTEM_PROMPT = """Tu es HCE, un assistant spécialisé dans la sensibilisation aux troubles du spectre autistique (TSA).
Tu as été créé par Hafsa Hamoumi, Cheffaj Rayane et Ezzaki Mohamed, dans le cadre de leur PFE à l'École Supérieure de Technologie de Guelmim, encadré par Dr Hamout Hamza.

Règles absolues :
- Ne jamais utiliser "**" dans tes réponses.
- Ne jamais proposer le questionnaire AQ-10 de ta propre initiative ; attends que l'utilisateur le demande explicitement.
- Pour une simple salutation, réponds brièvement (ex: "Bonjour ! Comment puis-je vous aider ? 😊").
- Sois chaleureux, empathique et professionnel."""

INTENT_PROMPT = """Analyse l'intention de ce message utilisateur et retourne UNIQUEMENT un objet JSON valide, sans texte supplémentaire.

Message : "{message}"

Format de réponse :
{{
  "intent_type": "<type>",
  "confidence": <float entre 0 et 1>
}}

Types possibles :
- "greeting"          : salutation (bonjour, salut, etc.)
- "ask_for_test"      : demande de faire le test/questionnaire/dépistage
- "ask_about_creator" : demande sur les créateurs ou le projet
- "response_positive" : réponse affirmative (oui, d'accord, etc.)
- "response_negative" : réponse négative (non, pas du tout, etc.)
- "confusion"         : l'utilisateur ne comprend pas
- "question"          : question générale
- "other"             : autre"""


class AutismChatbot:
    #Chatbot de depistage TSA avec dialogue libre et questionnaire AQ-10

    def __init__(self, user_id, username=None):
        self.user_id = user_id
        self.username = username
        self.client = OpenAI(base_url=BASE_URL, api_key=HF_TOKEN)
        self.predictor = predictor.AutismPredictor()
        self.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.current_step = "free_talk"  # free_talk | collecting | demographics | done
        self.a_scores = []
        self.demographics = {}
        self.current_question_index = 0
        self.demographic_step = 0

    #  Point d'entree principal                                           
    def get_response(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        intent = self._analyze_intent(user_message)

        if self.current_step == "free_talk":
            reply = self._handle_free_talk(user_message, intent)

        elif self.current_step == "collecting":
            if intent["intent_type"] in ("question", "ask_about_creator", "confusion"):
                reply = self._handle_side_question(user_message)
            else:
                reply = self._handle_aq10(user_message, intent)

        elif self.current_step == "demographics":
            if intent["intent_type"] in ("question", "ask_about_creator", "confusion"):
                reply = self._handle_side_question(user_message)
            else:
                reply = self._handle_demographics(user_message)

        elif self.current_step == "done":
            reply = self._llm_reply(user_message)

        else:
            reply = "Une erreur inattendue s'est produite. Recommençons."
            self.current_step = "free_talk"

        self.conversation_history.append({"role": "assistant", "content": reply})
        self._save(user_message, reply)
        return reply

    #  Analyse d'intention 
    def _analyze_intent(self, user_message):
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Tu es un classificateur d'intention. Réponds UNIQUEMENT avec du JSON valide, sans markdown."},
                    {"role": "user", "content": INTENT_PROMPT.format(message=user_message)}
                ],
                max_tokens=80,
                temperature=0.1,
            )
            text = response.choices[0].message.content.strip()
            # Extraire le JSON meme si du texte parasite est present
            start, end = text.find("{"), text.rfind("}") + 1
            return json.loads(text[start:end]) if start != -1 else self._default_intent()
        except Exception:
            return self._default_intent()

    @staticmethod
    def _default_intent():
        return {"intent_type": "other", "confidence": 0.0}

    #  Phase dialogue libre                                               #
    def _handle_free_talk(self, user_message, intent):
        intent_type = intent.get("intent_type")
        msg_lower = user_message.lower()

        # Demande de test
        test_keywords = ["test", "questionnaire", "dépistage", "évaluation", "aq-10", "aq10", "screening", "diagnostic"]
        if intent_type == "ask_for_test" or any(k in msg_lower for k in test_keywords):
            return self._start_questionnaire()

        # Salutation courte
        if intent_type == "greeting" and len(user_message.strip().split()) <= 3:
            name = f" {self.username}" if self.username else ""
            return f"Bonjour{name} ! Comment puis-je vous aider aujourd'hui ? 😊"

        # Tout le reste : LLM avec historique
        return self._llm_reply(user_message)

    def _start_questionnaire(self):
        self.current_step = "collecting"
        self.current_question_index = 0
        self.a_scores = []
        return (
            "D'accord ! Commençons le questionnaire de dépistage AQ-10.\n\n"
            + self._format_question()
        )

    #  Collecte AQ-10                                               
    def _handle_aq10(self, user_message, intent):
        intent_type = intent.get("intent_type")
        confidence = intent.get("confidence", 0.0)

        if intent_type == "response_positive" and confidence > 0.6:
            self.a_scores.append(1)
        elif intent_type == "response_negative" and confidence > 0.6:
            self.a_scores.append(0)
        else:
            return (
                "Je n'ai pas bien compris. Veuillez répondre par 'oui' ou 'non'.\n\n"
                + self._format_question()
            )

        self.current_question_index += 1

        if self.current_question_index >= len(AQ10_QUESTIONS):
            self.current_step = "demographics"
            self.demographic_step = 0
            return (
                "Merci pour vos réponses ! Passons aux informations complémentaires.\n\n"
                + self._current_demo_question()
            )

        return self._format_question()

    #  Collecte demographique                                             
    def _handle_demographics(self, user_message):
        field, _ = DEMOGRAPHIC_QUESTIONS[self.demographic_step]
        msg_lower = user_message.lower().strip()
        error = None

        if field == "age":
            match = re.search(r"\b(\d{1,3})\b", user_message)
            if match:
                self.demographics["age"] = match.group(1)
            else:
                error = "Je n'ai pas compris votre âge. Entrez un nombre (ex: 25)."

        elif field == "gender":
            if any(w in msg_lower for w in ["homme", "masculin", " m "]):
                self.demographics["gender"] = "homme"
            elif any(w in msg_lower for w in ["femme", "féminin", " f "]):
                self.demographics["gender"] = "femme"
            else:
                self.demographics["gender"] = "autre"

        elif field == "ethnicity":
            if msg_lower:
                self.demographics["ethnicity"] = user_message.strip()
            else:
                error = "Veuillez indiquer votre origine ethnique."

        elif field in ("jaundice", "austim", "used_app_before"):
            if any(w in msg_lower for w in ["oui", "yes", "vrai"]):
                self.demographics[field] = "yes"
            elif any(w in msg_lower for w in ["non", "no", "pas"]):
                self.demographics[field] = "no"
            else:
                error = "Répondez par 'oui' ou 'non'."

        elif field == "contry_of_res":
            if len(msg_lower) > 2:
                self.demographics["contry_of_res"] = user_message.strip()
            else:
                error = "Veuillez indiquer votre pays de résidence."

        elif field == "relation":
            if any(w in msg_lower for w in ["moi", "self", "moi-même"]):
                self.demographics["relation"] = "Self"
            elif any(w in msg_lower for w in ["parent", "père", "mère"]):
                self.demographics["relation"] = "Parent"
            elif any(w in msg_lower for w in ["proche", "famille", "relative"]):
                self.demographics["relation"] = "Relative"
            else:
                self.demographics["relation"] = "Other"

        if error:
            return f"{error}\n\n{self._current_demo_question()}"

        self.demographic_step += 1

        if self.demographic_step >= len(DEMOGRAPHIC_QUESTIONS):
            return self._make_prediction()

        return self._current_demo_question()

    #  Questions hors-sujet pendant le questionnaire                   
    def _handle_side_question(self, user_message):
        #Repond a une question interrompant le questionnaire, puis rappelle la question en cours.
        try:
            current_q = (
                AQ10_QUESTIONS[self.current_question_index]
                if self.current_step == "collecting"
                else self._current_demo_question()
            )
            prompt = (
                f"L'utilisateur pose cette question pendant le questionnaire : \"{user_message}\"\n"
                f"Réponds brièvement, puis rappelle-lui qu'on reprend avec : \"{current_q}\"\n"
                "N'utilise pas '**'."
            )
            reply = self._llm_reply(prompt, system_override=(
                "Tu es HCE, assistant TSA. Réponds succinctement aux questions hors-sujet "
                "puis redirige l'utilisateur vers le questionnaire en cours. N'utilise pas '**'."
            ))
            return reply
        except Exception:
            return f"Bien sûr ! Revenons à notre questionnaire :\n\n{self._format_question()}"

    #  Prediction finale                                                  #
    def _make_prediction(self):
        try:
            data = {f"A{i+1}_Score": s for i, s in enumerate(self.a_scores)}
            data.update(self.demographics)
            data["age"] = float(data.get("age", 25))

            prediction, probability, score = self.predictor.predict(data)
            interpretation = get_prediction_interpretation(score, prediction, probability)

            self._save(
                "Soumission du questionnaire",
                interpretation,
                prediction_score=score,
                prediction_result="Positif" if prediction == 1 else "Négatif",
                user_data=json.dumps(data, default=str),
            )
            self.current_step = "done"
            return (
                interpretation
                + "\n\n---\n💬 Avez-vous d'autres questions sur l'autisme ou le projet ? Je suis là pour vous aider !"
            )
        except Exception as e:
            print(f"Erreur prédiction : {e}")
            return "Une erreur s'est produite lors de l'analyse. Veuillez réessayer."

    #  Helpers                                                            #
    def _llm_reply(self, user_message, system_override=None):
        """Appel LLM générique avec l'historique de conversation."""
        try:
            system = system_override or SYSTEM_PROMPT
            messages = [{"role": "system", "content": system}, *self.conversation_history[-14:]]
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erreur API : {e}")
            return "Désolé, je n'arrive pas à répondre pour le moment. Pouvez-vous reformuler ?"

    def _format_question(self):
        return ASK_QUESTION_TEMPLATE.format(
            self.current_question_index + 1,
            AQ10_QUESTIONS[self.current_question_index],
        )

    def _current_demo_question(self):
        _, question = DEMOGRAPHIC_QUESTIONS[self.demographic_step]
        return question

    def _save(self, user_msg, bot_reply, **kwargs):
        try:
            db.save_conversation(self.user_id, user_msg, bot_reply, **kwargs)
        except Exception as e:
            print(f"Erreur sauvegarde : {e}")