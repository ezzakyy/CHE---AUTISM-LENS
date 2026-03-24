# config.py

import os

# ==================== Configuration de l'API Hugging Face ====================
HF_TOKEN = "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"
BASE_URL = "https://router.huggingface.co/v1"
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

# ==================== Configuration du modèle et des données ====================
DATA_PATH = 'data/'
TRAIN_FILE = DATA_PATH + 'train.csv'
SAVED_MODELS_DIR = 'saved_models/'
BEST_MODEL_PATH = SAVED_MODELS_DIR + 'best_model.pkl'
SCALER_PATH = SAVED_MODELS_DIR + 'scaler.pkl'
ENCODER_PATH = SAVED_MODELS_DIR + 'encoders.pkl'

# config.py (ajouter à la fin)
MODEL_RECALL = 0.98      # Exemple : rappel du modèle
MODEL_PRECISION = 0.89   # Exemple : précision
SCHOOL_LOGO_PATH = "logo_estg.png"  # Chemin vers le logo (à placer dans le dossier)

# Noms des colonnes
SCORES = ['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score',
          'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score']
DEMOGRAPHIC_FEATURES = ['age', 'gender', 'ethnicity', 'jaundice', 'austim',
                         'contry_of_res', 'used_app_before', 'relation']

ALL_FEATURES = SCORES + DEMOGRAPHIC_FEATURES

# ==================== Configuration de la base de données ====================
DATABASE_NAME = "autism_screening.db"
USERS_TABLE = "users"
CONVERSATIONS_TABLE = "conversations"

# ==================== Configuration du chatbot ====================
MAX_TOKENS = 800
TEMPERATURE = 0.7
TOP_P = 0.9

# Constantes de l'application
APP_TITLE = "CHE ~ AUTISM LENS "
APP_ICON = "🧠"

# Couleurs du thème ChatGPT
PRIMARY_COLOR = "#10a37f"
PRIMARY_HOVER = "#0d8c6c"
SIDEBAR_BG = "#f9fafc"
MAIN_BG = "#ffffff"
USER_MESSAGE_BG = "#10a37f"
BOT_MESSAGE_BG = "#f7f7f9"
TEXT_PRIMARY = "#1f1f2b"
TEXT_SECONDARY = "#70707c"
BORDER_COLOR = "#e5e7eb"

# Messages
ERROR_MESSAGE_MODEL = "Désolé, le modèle n'est pas disponible actuellement. Veuillez réessayer plus tard !"
GREETING_MESSAGE = """Bonjour ! Je suis HCE votre assistant spécialisé dans l'évaluation des risques de TSA. 

Je vais vous guider à travers un questionnaire de 10 questions et recueillir quelques informations démographiques. 
N'hésitez pas à me demander des explications sur n'importe quelle question !

Êtes-vous prêt à commencer ? Répondez simplement par 'oui' quand vous voulez débuter."""

# Template pour le système prompt
SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant médical spécialisé dans la sensibilisation aux troubles du spectre autistique (TSA). Ton nom est 'Assistant TSA'.

Tu dois guider l'utilisateur à travers un questionnaire de dépistage AQ-10 de manière naturelle et empathique.

RÈGLES IMPORTANTES:
1. Commence par te présenter et demander si l'utilisateur est prêt à commencer.
2. Pose une question à la fois.
3. Si l'utilisateur ne comprend pas une question, explique-la simplement.
4. Pour chaque question AQ-10, attends une réponse (oui/non). Si la réponse n'est pas claire, demande poliment de préciser.
5. Après les 10 questions, demande les informations démographiques dans cet ordre: âge, sexe, origine ethnique, jaunisse à la naissance, antécédents familiaux d'autisme, pays de résidence, utilisation antérieure d'applis similaires, lien avec la personne évaluée.
6. Une fois toutes les données collectées, dis "Merci pour vos réponses ! Je vais maintenant analyser vos résultats."
7. Après avoir reçu l'analyse du système, explique les résultats à l'utilisateur de manière claire et bienveillante, sans utiliser le mot "diagnostic".
8. Reste disponible pour répondre aux questions après l'analyse.

Liste des questions AQ-10:
{questions_liste}

Sois chaleureux, patient et professionnel. Adapte ton langage à l'utilisateur."""

ASK_QUESTION_TEMPLATE = "Question {}/10 : {}"