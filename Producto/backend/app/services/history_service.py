import uuid
from datetime import UTC, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan_entity import ScanEntity
from app.schemas.scan_result import ScanResult


class HistoryService:
    async def save(
        self, scan: ScanResult, user_id: str, session: AsyncSession
    ) -> ScanEntity:
        """Persiste un ScanResult en la BD y retorna la entidad con el scan_id asignado."""
        entity = ScanEntity(
            scan_id=str(uuid.uuid4()),
            user_token=user_id,   # reutilizamos user_token para almacenar el user_id
            fruit_type=scan.fruit_type,
            maturity_label=scan.maturity_label,
            confidence=scan.confidence,
            bbox=scan.bbox,
            recommendation=scan.recommendation,
            color_code=scan.color_code,
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    async def get_all(
        self,
        user_id: str,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ScanResult], int]:
        total: int = (
            await session.execute(
                select(func.count())
                .select_from(ScanEntity)
                .where(ScanEntity.user_token == user_id)
            )
        ).scalar_one()

        rows = (
            await session.execute(
                select(ScanEntity)
                .where(ScanEntity.user_token == user_id)
                .order_by(ScanEntity.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        ).scalars().all()

        items = [
            ScanResult(
                scan_id=e.scan_id,
                fruit_type=e.fruit_type,
                maturity_label=e.maturity_label,
                confidence=e.confidence,
                bbox=e.bbox,
                recommendation=e.recommendation,
                color_code=e.color_code,
            )
            for e in rows
        ]
        return items, total
