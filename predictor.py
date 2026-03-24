import joblib
from config import BEST_MODEL_PATH
import utils

class AutismPredictor:
    #Classe pour gerer le chargement du modele et faire des predictions

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.load_model()

    def load_model(self):
        #Charger le modele et les outils de pretraitement.
        try:
            self.model = joblib.load(BEST_MODEL_PATH)
            self.scaler, self.encoders = utils.load_preprocessing_objects()
            print("Modele et outils charges avec succes.")
        except FileNotFoundError as e:
            print(f"Erreur de chargement : {e}")
            self.model = None
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            self.model = None

    def predict(self, user_data_dict):
        
        #Predire le risque de TSA
        if self.model is None:
            raise Exception("Le modele n'est pas charge.")

        processed_features = utils.preprocess_user_input(user_data_dict, self.scaler, self.encoders)
        responses = [user_data_dict.get(f'A{i}_Score', 0) for i in range(1, 11)]
        score = utils.calculate_score_from_responses(responses)

        prediction = self.model.predict(processed_features)[0]
        probability = self.model.predict_proba(processed_features)[0][1]

        return prediction, probability, score