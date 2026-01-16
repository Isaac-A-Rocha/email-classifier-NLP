from transformers import pipeline
from app.services.classifier import classify
from app.services.preprocessing import clean_text, is_likely_email

# Mantemos o gerador apenas como fallback (opcional)
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    max_length=80,
    do_sample=False
)

def generate_reply(category, intent, text):
    # ESTRATÉGIA DE TEMPLATES: Respostas profissionais e garantidas em Português
    templates = {
        "Improdutivo": (
            "Agradecemos o seu contato. No momento, esta mensagem foi classificada como informativa. "
            "Caso necessite de suporte específico, por favor, entre em contato através dos nossos canais oficiais."
        ),
        "Suporte": (
            "Recebemos sua solicitação de suporte técnico. Nossa equipe especializada já foi acionada "
            "para analisar o problema relatado e retornaremos com uma solução o mais breve possível. "
            "Protocolo de atendimento gerado automaticamente."
        ),
        "Financeiro": (
            "Prezado(a), sua solicitação financeira foi encaminhada para o setor de contas e faturamento. "
            "Aguarde o prazo de até 24h úteis para uma posição detalhada sobre sua demanda."
        ),
        "Comercial": (
            "Obrigado pelo interesse! Encaminhamos sua mensagem para um de nossos consultores comerciais. "
            "Em breve entraremos em contato para dar continuidade ao seu atendimento."
        ),
        "Outro": (
            "Agradecemos sua mensagem. Ela foi recebida por nossa triagem automática e será "
            "direcionada ao departamento responsável para análise."
        )
    }

    # Se for improdutivo, retorna direto o template
    if category == "Improdutivo":
        return templates["Improdutivo"]

    # Busca o template baseado na intenção, se não achar usa "Outro"
    reply = templates.get(intent, templates["Outro"])
    
    return reply

def build_response(text: str):
    cleaned = clean_text(text)

    # Valida se parece email
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

    # Chama seu classificador de Machine Learning (que já está funcionando!)
    result = classify(text, cleaned)

    # Gera a resposta usando os templates seguros
    reply = generate_reply(
        result["category"],
        result["intent"],
        text[:400]
    )

    return {
        "category": result["category"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "suggested_reply": reply,
        "source": result["source"],
    }