import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import UserInfo
from app.schemas.scan_result import PredictResponse, ScanResult
from app.services.auth_service import get_current_user
from app.services.history_service import HistoryService
from app.services.inference_service import InferenceService

router = APIRouter(tags=["Inferencia"])
inference_svc = InferenceService()
history_svc = HistoryService()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_FRUITS = {"aguacate_hass", "platano", "tomate_usda", "mango"}


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: Request,
    file: UploadFile = File(...),
    fruit_type: str | None = Form(default=None),
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PredictResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado")

    if fruit_type is not None and fruit_type not in ALLOWED_FRUITS:
        raise HTTPException(
            status_code=400,
            detail=f"fruit_type inválido. Valores permitidos: {sorted(ALLOWED_FRUITS)}",
        )

    model = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    image_bytes = await file.read()

    result: ScanResult | None = await asyncio.to_thread(
        inference_svc.run, image_bytes, model, fruit_type
    )

    if result is None:
        msg = (
            f"No se detectó {fruit_type} en la imagen"
            if fruit_type else "No se detectó ninguna fruta soportada"
        )
        return PredictResponse(success=False, error=msg)

    # Persistir y obtener el scan_id
    entity = await history_svc.save(result, current_user.user_id, db)
    result.scan_id = entity.scan_id

    return PredictResponse(success=True, data=result)
