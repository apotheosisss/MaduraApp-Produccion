import io

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import MagicMock

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


def make_jpeg_bytes(color: tuple = (128, 200, 50)) -> bytes:
    img = Image.new("RGB", (100, 100), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest_asyncio.fixture(scope="module")
async def client():
    from app.core.database import Base, get_db
    from app.main import app

    test_engine = create_async_engine(TEST_DB_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.state.model = MagicMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def auth_headers(client: AsyncClient) -> dict:
    """Registra un usuario de prueba y retorna las cabeceras de autenticación."""
    resp = await client.post(
        "/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@maduraapp.cl",
            "password": "testpassword123",
        },
    )
    # Si el usuario ya existe (otro test lo creó) intentamos login
    if resp.status_code == 409:
        resp = await client.post(
            "/v1/auth/login",
            json={"email": "test@maduraapp.cl", "password": "testpassword123"},
        )

    assert resp.status_code in (200, 201), f"Auth falló: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
