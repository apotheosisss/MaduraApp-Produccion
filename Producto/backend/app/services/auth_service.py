"""Servicio de autenticación: registro, login y verificación de tokens JWT."""
import uuid
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.user_entity import UserEntity
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserInfo

bearer_scheme = HTTPBearer()


class AuthService:
    async def register(
        self,
        data: RegisterRequest,
        session: AsyncSession,
    ) -> AuthResponse:
        # Verificar que el username y email no estén en uso
        existing = (
            await session.execute(
                select(UserEntity).where(
                    (UserEntity.username == data.username)
                    | (UserEntity.email == data.email)
                )
            )
        ).scalar_one_or_none()

        if existing:
            if existing.username == data.username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El nombre de usuario ya está en uso.",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado.",
            )

        user = UserEntity(
            user_id=str(uuid.uuid4()),
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            created_at=datetime.now(UTC),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(user.user_id, user.username)
        return AuthResponse(
            access_token=token,
            user_id=user.user_id,
            username=user.username,
        )

    async def login(
        self,
        data: LoginRequest,
        session: AsyncSession,
    ) -> AuthResponse:
        user = (
            await session.execute(
                select(UserEntity).where(UserEntity.email == data.email)
            )
        ).scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada.",
            )

        token = create_access_token(user.user_id, user.username)
        return AuthResponse(
            access_token=token,
            user_id=user.user_id,
            username=user.username,
        )


# ── Dependency de autenticación ──────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserInfo:
    """Dependency de FastAPI que verifica el JWT y retorna la info del usuario."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if not user_id:
            raise JWTError("sin sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (
        await session.execute(select(UserEntity).where(UserEntity.user_id == user_id))
    ).scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado.",
        )

    return UserInfo(user_id=user.user_id, username=user.username, email=user.email)
