import os  
import nltk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  
from fastapi.responses import FileResponse   
from app.api.routes import router

# Downloads necessários para o processamento de texto
nltk.download('stopwords')
nltk.download('rslp')
nltk.download('punkt')

app = FastAPI(title="Email Classifier API")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API 
app.include_router(router)
if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def serve_index():
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "API rodando", "aviso": "Frontend não encontrado. Verifique se a pasta frontend está na raiz."}