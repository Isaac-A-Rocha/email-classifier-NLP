import pandas as pd
import joblib
import os
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

#Preparação de Stop Words
try:
    nltk.download('stopwords')
    pt_stopwords = stopwords.words('portuguese')
except Exception:
    pt_stopwords = ['de', 'a', 'o', 'que', 'em', 'do', 'da', 'um', 'para', 'com']

# Caminhos de Arquivos 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "emails.csv") 

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Arquivo não encontrado: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
from app.services.preprocessing import clean_text

X = df["text"].apply(clean_text)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y # stratify mantém a proporção de labels
)

# 4. Pipeline Otimizado
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words=pt_stopwords,
        ngram_range=(1, 2), # Analisa palavras únicas E pares de palavras 
        max_features=5000   
    )),
    ("clf", LogisticRegression(
        max_iter=1000, 
        class_weight='balanced' 
    ))
])

#Execução 
print(f"Treinando com {len(df)} exemplos...")
pipeline.fit(X_train, y_train)

#Avaliação 
y_pred = pipeline.predict(X_test)
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)

print("\nMatriz de Confusão:")
print(cm)

acc = accuracy_score(y_test, y_pred)
print(f"\nAcurácia Total: {acc:.2%}")
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))

MODEL_SAVE_PATH = os.path.join(BASE_DIR, "model.joblib")
joblib.dump(pipeline, MODEL_SAVE_PATH)

print(f"\n Sucesso! Modelo treinado e salvo em: {MODEL_SAVE_PATH}")