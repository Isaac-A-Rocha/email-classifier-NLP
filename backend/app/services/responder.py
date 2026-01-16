from app.services.classifier import classify
from app.services.preprocessing import clean_text, is_likely_email

def generate_reply(category, intent):
    templates = {
        "Improdutivo": (
            "Agradecemos o contato. Caso tenha uma solicitação específica, "
            "por favor envie mais informações para nossa equipe."
        ),
        "Suporte": (
            "Recebemos sua solicitação de suporte técnico. Nossa equipe irá analisar "
            "o problema e retornaremos em breve com orientações."
        ),
        "Financeiro": (
            "Sua solicitação financeira foi encaminhada ao setor responsável. "
            "Em até 24h úteis retornaremos com uma posição."
        ),
        "Comercial": (
            "Obrigado pelo interesse. Um de nossos consultores comerciais "
            "entrará em contato em breve."
        ),
        "Outro": (
            "Sua mensagem foi recebida e será direcionada ao setor responsável."
        )
    }

    if category == "Improdutivo":
        return templates["Improdutivo"]

    return templates.get(intent, templates["Outro"])


def build_response(text: str):
    cleaned = clean_text(text)

    if not is_likely_email(text.lower()):
        return {
            "category": "Improdutivo",
            "intent": "Outro",
            "confidence": 0.9,
            "suggested_reply": (
                "Agradecemos o contato. Caso tenha uma solicitação específica, "
                "por favor envie mais informações para nossa equipe."
            ),
            "source": "rules"
        }

    result = classify(text, cleaned)

    reply = generate_reply(result["category"], result["intent"])

    return {
        "category": result["category"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "suggested_reply": reply,
        "source": result["source"],
    }
