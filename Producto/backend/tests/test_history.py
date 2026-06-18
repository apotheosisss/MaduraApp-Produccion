from unittest.mock import patch

from httpx import AsyncClient

from app.schemas.scan_result import ScanResult
from tests.conftest import make_jpeg_bytes

MOCK_SCAN = ScanResult(
    fruit_type="platano",
    maturity_label="INMADURO",
    confidence=0.78,
    bbox=[5.0, 10.0, 200.0, 300.0],
    recommendation="Madurar en bolsa de papel 2-3 días",
    color_code="green",
)


async def test_history_requires_auth(client: AsyncClient):
    """Sin token se debe rechazar con 401."""
    r = await client.get("/v1/history")
    assert r.status_code == 401


async def test_history_empty_for_new_user(client: AsyncClient):
    """Un usuario recién registrado tiene historial vacío."""
    # Registrar usuario único para este test
    resp = await client.post(
        "/v1/auth/register",
        json={
            "username": "historyuser",
            "email": "history@maduraapp.cl",
            "password": "password123",
        },
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.get("/v1/history", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0


async def test_history_after_predict(client: AsyncClient, auth_headers: dict):
    """El historial incluye los escaneos del usuario autenticado."""
    with patch("app.routers.predict.inference_svc.run", return_value=MOCK_SCAN):
        await client.post(
            "/v1/predict",
            files={"file": ("banana.jpg", make_jpeg_bytes((200, 230, 100)), "image/jpeg")},
            headers=auth_headers,
        )

    r = await client.get("/v1/history", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    items = data["items"]
    assert len(items) >= 1
    assert items[0]["fruit_type"] == "platano"
    assert items[0]["maturity_label"] == "INMADURO"
    assert items[0]["scan_id"] is not None


async def test_history_pagination(client: AsyncClient, auth_headers: dict):
    r = await client.get("/v1/history?limit=5&offset=0", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert len(data["items"]) <= 5


async def test_history_limit_validation(client: AsyncClient, auth_headers: dict):
    r = await client.get("/v1/history?limit=200", headers=auth_headers)
    assert r.status_code == 422


async def test_auth_register_duplicate(client: AsyncClient):
    """No se puede registrar dos veces el mismo email."""
    body = {"username": "dupuser", "email": "dup@maduraapp.cl", "password": "duppass123"}
    await client.post("/v1/auth/register", json=body)
    r = await client.post("/v1/auth/register", json=body)
    assert r.status_code == 409


async def test_auth_register_weak_password(client: AsyncClient):
    """Contraseña corta o sin número se rechaza (OWASP A07)."""
    corta = {"username": "weak1", "email": "weak1@maduraapp.cl", "password": "ab1"}
    assert (await client.post("/v1/auth/register", json=corta)).status_code == 422

    sin_numero = {"username": "weak2", "email": "weak2@maduraapp.cl", "password": "onlyletters"}
    assert (await client.post("/v1/auth/register", json=sin_numero)).status_code == 422


async def test_auth_login_wrong_password(client: AsyncClient):
    body = {"email": "test@maduraapp.cl", "password": "wrongpassword"}
    r = await client.post("/v1/auth/login", json=body)
    assert r.status_code == 401


async def test_feedback_submit(client: AsyncClient, auth_headers: dict):
    """Envío de feedback (rating) para un escaneo existente."""
    # Crear un escaneo primero
    with patch("app.routers.predict.inference_svc.run", return_value=MOCK_SCAN):
        predict_resp = await client.post(
            "/v1/predict",
            files={"file": ("banana.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers=auth_headers,
        )
    scan_id = predict_resp.json()["data"]["scan_id"]

    # Enviar feedback
    r = await client.post(
        "/v1/feedback",
        json={"scan_id": scan_id, "rating": 4},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["success"] is True
    assert data["feedback_id"] > 0


async def test_feedback_invalid_rating(client: AsyncClient, auth_headers: dict):
    """Rating fuera de rango debe ser rechazado."""
    r = await client.post(
        "/v1/feedback",
        json={"scan_id": "fake-id", "rating": 6},
        headers=auth_headers,
    )
    assert r.status_code == 422
