from unittest.mock import patch

from httpx import AsyncClient

from app.schemas.scan_result import ScanResult
from tests.conftest import make_jpeg_bytes

MOCK_SCAN = ScanResult(
    fruit_type="mango",
    maturity_label="OPTIMO",
    confidence=0.92,
    bbox=[10.0, 20.0, 300.0, 400.0],
    recommendation="Consumir hoy, refrigerar si no lo consumes",
    color_code="yellow",
)


async def test_health(client: AsyncClient):
    """El health check es público — no requiere autenticación."""
    r = await client.get("/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data


async def test_predict_requires_auth(client: AsyncClient):
    """Sin token se debe rechazar con 401."""
    r = await client.post(
        "/v1/predict",
        files={"file": ("img.jpg", make_jpeg_bytes(), "image/jpeg")},
    )
    assert r.status_code == 401


async def test_predict_unsupported_format(client: AsyncClient, auth_headers: dict):
    r = await client.post(
        "/v1/predict",
        files={"file": ("img.gif", b"GIF89a", "image/gif")},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "no soportado" in r.json()["detail"]


async def test_predict_invalid_fruit_type(client: AsyncClient, auth_headers: dict):
    r = await client.post(
        "/v1/predict",
        files={"file": ("img.jpg", make_jpeg_bytes(), "image/jpeg")},
        data={"fruit_type": "manzana"},
        headers=auth_headers,
    )
    assert r.status_code == 400


async def test_predict_no_detection(client: AsyncClient, auth_headers: dict):
    with patch("app.routers.predict.inference_svc.run", return_value=None):
        r = await client.post(
            "/v1/predict",
            files={"file": ("fruit.jpg", make_jpeg_bytes(), "image/jpeg")},
            headers=auth_headers,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert "error" in data


async def test_predict_with_detection(client: AsyncClient, auth_headers: dict):
    with patch("app.routers.predict.inference_svc.run", return_value=MOCK_SCAN):
        r = await client.post(
            "/v1/predict",
            files={"file": ("mango.jpg", make_jpeg_bytes((255, 200, 0)), "image/jpeg")},
            headers=auth_headers,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    result = data["data"]
    assert result["fruit_type"] == "mango"
    assert result["maturity_label"] == "OPTIMO"
    assert result["color_code"] == "yellow"
    assert result["scan_id"] is not None   # el scan_id debe ser retornado
    assert isinstance(result["confidence"], float)
    assert len(result["bbox"]) == 4


async def test_predict_with_fruit_filter(client: AsyncClient, auth_headers: dict):
    with patch("app.routers.predict.inference_svc.run", return_value=MOCK_SCAN):
        r = await client.post(
            "/v1/predict",
            files={"file": ("mango.jpg", make_jpeg_bytes((255, 200, 0)), "image/jpeg")},
            data={"fruit_type": "mango"},
            headers=auth_headers,
        )
    assert r.status_code == 200
    assert r.json()["success"] is True
