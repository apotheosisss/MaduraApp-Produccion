from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    scan_id: str
    rating: int = Field(..., ge=1, le=5, description="Calificación del escaneo de 1 (pésimo) a 5 (excelente)")


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: int
    message: str = "¡Gracias por tu feedback!"
