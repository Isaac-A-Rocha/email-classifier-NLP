import re
from typing import List
from unidecode import unidecode
import nltk


try:
    from nltk.corpus import stopwords
    PT_STOPWORDS = set(stopwords.words("portuguese"))
except Exception:
    PT_STOPWORDS = set([
        "de","a","o","que","em","do","da","um","para","com","is","e","no","na"
    ])

try:
    STEMMER = nltk.stem.RSLPStemmer()
except Exception:
    STEMMER = None


EMAIL_RE = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"
PHONE_RE = r"\+?\d[\d\-\s\(\)]{6,}\d"
URL_RE = r"https?:\/\/\S+|www\.\S+"
NON_ALPHA_RE = r"[^a-z0-9\s]"

def normalize_text(text: str) -> str:
    """Lowercase, remove accents, normalize whitespace."""
    if not text:
        return ""
    text = text.strip()
    text = unidecode(text)  
    text = text.lower()
    text = re.sub(EMAIL_RE, " ", text)
    text = re.sub(PHONE_RE, " ", text)
    text = re.sub(URL_RE, " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    text = re.sub(NON_ALPHA_RE, " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t and t not in PT_STOPWORDS]
    if STEMMER:
        try:
            tokens = [STEMMER.stem(t) for t in tokens]
        except Exception:
            pass
    return tokens

def clean_text(text: str) -> str:
    """Return normalized, cleaned text (string) — best for ML and rules if needed."""
    norm = normalize_text(text)
    tokens = tokenize(norm)
    return " ".join(tokens)

def tokens_for_rules(text: str):
    """Return normalized tokens (not stemmed) to use for rules matching if you prefer."""
    norm = normalize_text(text)
    return norm.split()

def extract_text_features(text: str) -> dict:
    words = text.split()
    word_count = len(words)

    verbs = [
        "preciso", "solicito", "gostaria", "poderia", "poderiam",
        "aguardo", "informar", "resolver", "verificar"
    ]

    greetings = ["ola", "bom dia", "boa tarde", "prezado"]

    verb_hits = sum(1 for v in verbs if v in text)
    greet_hits = sum(1 for g in greetings if g in text)

    numbers_ratio = sum(1 for c in text if c.isdigit()) / max(len(text), 1)

    return {
        "word_count": word_count,
        "verb_hits": verb_hits,
        "greet_hits": greet_hits,
        "numbers_ratio": numbers_ratio
    }

def is_likely_email(text: str) -> bool:
    feats = extract_text_features(text)

    if feats["word_count"] < 8:
        return False

    if feats["word_count"] > 250 and feats["verb_hits"] == 0:
        return False

 
    if feats["verb_hits"] == 0 and feats["greet_hits"] == 0:
        return False

    return True
