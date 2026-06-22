from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService, get_current_user
from app.schemas.auth import UserInfo

router = APIRouter(prefix="/auth", tags=["Autenticación"])
svc = AuthService()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Registra un nuevo usuario y retorna un JWT listo para usar."""
    return await svc.register(body, db)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Autentica al usuario y retorna un JWT."""
    return await svc.login(body, db)


@router.get("/me", response_model=UserInfo)
async def me(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Retorna la información del usuario autenticado. Útil para verificar el token."""
    return current_user
