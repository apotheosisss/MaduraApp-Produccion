from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.feedback_entity import FeedbackEntity
from app.models.scan_entity import ScanEntity
from app.schemas.auth import UserInfo
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.auth_service import get_current_user

router = APIRouter(tags=["Feedback"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    body: FeedbackRequest,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """Envía una calificación (1-5 estrellas) para un escaneo.

    Permite al equipo analizar qué escaneos fueron incorrectos para
    mejorar el modelo en futuras iteraciones de entrenamiento.
    """
    # Verificar que el scan existe
    scan = (
        await db.execute(select(ScanEntity).where(ScanEntity.scan_id == body.scan_id))
    ).scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escaneo '{body.scan_id}' no encontrado.",
        )

    # Evitar feedback duplicado del mismo usuario para el mismo scan
    existing = (
        await db.execute(
            select(FeedbackEntity).where(
                (FeedbackEntity.scan_id == body.scan_id)
                & (FeedbackEntity.user_id == current_user.user_id)
            )
        )
    ).scalar_one_or_none()

    if existing:
        # Actualizar rating existente en vez de duplicar
        existing.rating = body.rating
        await db.commit()
        await db.refresh(existing)
        return FeedbackResponse(
            success=True,
            feedback_id=existing.feedback_id,
            message="Feedback actualizado. ¡Gracias!",
        )

    feedback = FeedbackEntity(
        scan_id=body.scan_id,
        user_id=current_user.user_id,
        rating=body.rating,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackResponse(
        success=True,
        feedback_id=feedback.feedback_id,
    )
