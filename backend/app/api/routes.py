from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.email import EmailInput, PredictionOut
from app.services.responder import build_response
from app.services.file_reader import read_pdf, read_txt, ScannedPDFError, InvalidPDFError
import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api", tags=["Classificação"])

@router.post("/classify", response_model=PredictionOut)
async def classify_email(data: EmailInput):
    try:
        full_content = f"{data.subject} {data.text}".strip()
        
        result = build_response(full_content)
        
        result["text"] = data.text
        return result
    except Exception as e:
        logging.error("Erro ao classificar texto", exc_info=True)

        raise HTTPException(status_code=500, detail="Erro interno ao processar o texto.")

@router.post("/classify-file", response_model=PredictionOut)
async def classify_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".txt"):
            text = read_txt(content)
        elif filename.endswith(".pdf"):
            text = read_pdf(content)
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado")

        if not text or len(text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Conteúdo insuficiente.")

        full_content = f"Arquivo: {filename} {text}"
        result = build_response(full_content)
        
        result["text"] = text
        return result

    except (ScannedPDFError, InvalidPDFError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"ERRO NO ARQUIVO: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar arquivo")