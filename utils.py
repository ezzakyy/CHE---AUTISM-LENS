import pandas as pd
import joblib
from config import SCALER_PATH, ENCODER_PATH, ALL_FEATURES

def load_preprocessing_objects():
    #Charger le scaler et les encodeurs sauvegardes
    scaler = joblib.load(SCALER_PATH)
    encoders = joblib.load(ENCODER_PATH)
    return scaler, encoders

def preprocess_user_input(user_data_dict, scaler, encoders):
    #Convertir les donnees utilisateur en matrice prete pour le modele

    df = pd.DataFrame([user_data_dict])

    for col in ALL_FEATURES:
        if col not in df.columns:
            df[col] = None

    for col, le in encoders.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if x in le.classes_ else 'others' if 'others' in le.classes_ else le.classes_[0])
            df[col] = le.transform(df[col])

    df = df[ALL_FEATURES].astype(float)
    df_scaled = scaler.transform(df)

    return df_scaled

def calculate_score_from_responses(responses):
    #Calculer le score total a partir des reponses de l'utilisateur 
    return sum(responses)

def get_prediction_interpretation(score, prediction_class, probability):
    #Creer un texte explicatif du resultat.

    probability_percent = probability * 100

    if prediction_class == 1:
        interpretation = (
            f"🔴 **Résultat : Indicateurs positifs (TSA)**\n\n"
            f"Score : **{score}/10** | Probabilité : **{probability_percent:.1f}%**\n\n"
            f"Sur la base de vos réponses, les résultats indiquent la présence d'indicateurs compatibles avec un trouble du spectre autistique. "
            f"⚠️ **Ceci n'est pas un diagnostic final**, mais un outil de dépistage préliminaire.\n\n"
            f"**Recommandation :** Je vous recommande vivement de consulter un professionnel de santé pour une évaluation complète."
        )
    else:
        interpretation = (
            f"🟢 **Résultat : Indicateurs faibles**\n\n"
            f"Score : **{score}/10** | Probabilité : **{probability_percent:.1f}%**\n\n"
            f"Les indicateurs observés sont faibles pour un trouble du spectre autistique. "
            f"Cependant, si vous avez des inquiétudes, n'hésitez pas à consulter un spécialiste.\n\n"
            f"ℹ️ Cette évaluation ne remplace pas un avis médical professionnel."
        )
    return interpretation
  