from unidecode import unidecode

RAW_INTENT_KEYWORDS = {
    "suporte": {
        "erro": 2, "problema": 2, "falha": 2, "bug": 2, "travando": 2,
        "não funciona": 2, "indisponível": 2, "lento": 2, "parou": 2,
        "ajuda": 1, "socorro": 1, "suporte": 1, "instrução": 1,
    },
    "status": {
        "status": 2, "andamento": 2, "atualização": 2, "protocolo": 2,
        "retorno": 1, "resposta": 1, "posicionamento": 1, "saber sobre": 1,
    },
    "pedido": {
        "informe": 4, "rendimentos": 4, "fatura": 3, "boleto": 3, "extrato": 3,
        "comprovante": 3, "irpf": 4, "imposto": 3,
        "requisição": 2, "solicitação": 2, "pedido": 2, "enviar": 1,
        "acesso": 1, "senha": 1, "login": 1, "alterar": 1,
    },
    "feedback": {
        "obrigado": 2, "parabéns": 2, "elogio": 2, "agradeço": 2,
        "sugestão": 1, "melhoria": 1, "ideia": 1,
    },
}

# Garante matching com clean_text
def _normalize_key(k: str) -> str:
    return unidecode(k).lower().strip()

INTENT_KEYWORDS = {}
for intent, kws in RAW_INTENT_KEYWORDS.items():
    INTENT_KEYWORDS[intent] = { _normalize_key(k): v for k, v in kws.items() }

PRODUCTIVE_INTENTS = {"suporte", "status", "pedido"}

def score_intents(text: str):
    """
    Retorna (scores, matches) onde:
    - scores: {intent: score}
    - matches: {intent: [matched_keywords_normalized]}
    """
    text_norm = unidecode(text).lower()
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    matches = {intent: [] for intent in INTENT_KEYWORDS}

    for intent, keywords in INTENT_KEYWORDS.items():
        for key, weight in keywords.items():
            if key in text_norm:
                scores[intent] += weight
                matches[intent].append(key)

    return scores, matches

def rule_based_classification(text: str, min_score=2):
    """
    Retorna: category, confidence, matched_terms
    """
    scores, matches = score_intents(text)
    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score < min_score:
        return None, 0.0, []

    category = "Produtivo" if best_intent in PRODUCTIVE_INTENTS else "Improdutivo"
    # confidence proporcional
    confidence = min(0.9, 0.5 + best_score * 0.1)
    return category, confidence, matches[best_intent]
