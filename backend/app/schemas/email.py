from pydantic import BaseModel, Field
from typing import Optional

class EmailInput(BaseModel):
    subject: Optional[str] = Field("", description="O assunto do e-mail")
    text: str = Field(..., min_length=5, description="O conteúdo textual do e-mail para classificação")

class PredictionOut(BaseModel):
    category: str
    intent: str
    confidence: float
    suggested_reply: str
    source: str
    explanation: Optional[str] = None
    text: Optional[str] = None
