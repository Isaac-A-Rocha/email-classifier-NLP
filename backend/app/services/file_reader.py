from pypdf import PdfReader
from io import BytesIO


class ScannedPDFError(Exception):
    pass


class InvalidPDFError(Exception):
    pass


def read_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def read_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes), strict=False)

    except Exception as e:
        print("ERRO AO ABRIR PDF:", e)
        raise InvalidPDFError("Arquivo PDF inválido ou corrompido")

    text = ""

    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        except Exception as e:
            print("ERRO AO EXTRAIR TEXTO DA PÁGINA:", e)

    if len(text.strip()) < 50:
        raise ScannedPDFError("PDF parece ser escaneado (imagem), sem texto extraível")

    return text.strip()
