import joblib
import os
from app.services.rules import score_intents
from app.services.preprocessing import extract_text_features

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "ml", "model.joblib")

try:
    ml_model = joblib.load(MODEL_PATH)
except Exception as e:
    print("Erro ao carregar modelo ML:", e)
    ml_model = None


MIN_RULE_SCORE = 2
ML_CONF_THRESHOLD = 0.50

print("Modelo ML carregado:", ml_model is not None)


def ml_predict(cleaned_text: str):
    if not ml_model:
        return None, None

    try:
        pred = ml_model.predict([cleaned_text])[0]
        probs = ml_model.predict_proba([cleaned_text])[0]
        return pred, float(max(probs))
    except Exception as e:
        print("ML predict error:", e)
        return None, None


def classify(original_text: str, cleaned_text: str) -> dict:

    feats = extract_text_features(original_text)

    scores, matches = score_intents(original_text)
    best_intent = max(scores, key=scores.get)

    action_bonus = 1 if feats["verb_hits"] >= 1 else 0
    final_rule_score = scores.get(best_intent, 0) + action_bonus

    if final_rule_score >= MIN_RULE_SCORE:
        intent = best_intent.capitalize()
    else:
        intent = "Outro"


    if intent == "Outro":
        rule_category = "Improdutivo"
    else:
        rule_category = "Produtivo"

    category = rule_category
    confidence = 0.55
    source = "rules"


    if ml_model:
        pred, ml_conf = ml_predict(cleaned_text)

        if pred is not None and ml_conf >= ML_CONF_THRESHOLD:
            category = pred.capitalize()
            confidence = round(ml_conf, 2)
            source = "ml_model"
        else:
            confidence = round(confidence, 2)

    return {
        "category": category,
        "intent": intent,
        "confidence": confidence,
        "source": source,
    }
