from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import UserInfo
from app.schemas.scan_result import HistoryResponse
from app.services.auth_service import get_current_user
from app.services.history_service import HistoryService

router = APIRouter(tags=["Historial"])
svc = HistoryService()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HistoryResponse:
    items, total = await svc.get_all(current_user.user_id, db, limit, offset)
    return HistoryResponse(items=items, total=total, limit=limit, offset=offset)
