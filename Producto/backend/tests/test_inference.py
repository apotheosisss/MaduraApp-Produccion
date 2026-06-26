"""Pruebas de verificación del ESTADO DE MADUREZ de la fruta (prioridad docente).

Verifican la lógica central que traduce una detección del modelo en un estado de
madurez con su color y recomendación, sin depender de los pesos del modelo (se
simula la salida de YOLO). Cubren:
  - Consistencia de los mapas clase -> (fruta, estado) / color / recomendación.
  - postprocess() devuelve el estado correcto para cada clase.
  - Selección por confianza, umbral y filtro de fruta.
"""
import pytest

from app.services.inference_service import (
    CLASS_MAP,
    COLOR_MAP,
    RECOMMENDATION_MAP,
    InferenceService,
)
from app.core.config import settings


# ── Dobles de prueba que imitan la salida de Ultralytics YOLO ──────────────────
class _FakeTensor:
    def __init__(self, vals):
        self._vals = vals

    def tolist(self):
        return self._vals


class _FakeBox:
    def __init__(self, conf: float, cls: int, xyxy=(10.0, 20.0, 300.0, 400.0)):
        self.conf = [conf]
        self.cls = [cls]
        self.xyxy = [_FakeTensor(list(xyxy))]


class _FakeResult:
    def __init__(self, boxes):
        self.boxes = boxes


def _results(*boxes):
    return [_FakeResult(list(boxes))]


svc = InferenceService()


# ── Consistencia de los mapas de estado ───────────────────────────────────────
def test_class_map_cubre_4_frutas_x_3_estados():
    assert len(CLASS_MAP) == 12
    frutas = {f for f, _ in CLASS_MAP.values()}
    estados = {e for _, e in CLASS_MAP.values()}
    assert frutas == {"aguacate_hass", "platano", "tomate_usda", "mango"}
    assert estados == {"INMADURO", "OPTIMO", "SOBRE_MADURO"}


def test_cada_estado_tiene_color_y_recomendacion():
    for fruit, state in CLASS_MAP.values():
        assert state in COLOR_MAP, f"falta color para {state}"
        assert (fruit, state) in RECOMMENDATION_MAP, f"falta recomendación para {fruit}/{state}"


def test_semaforo_color_por_estado():
    assert COLOR_MAP["INMADURO"] == "green"
    assert COLOR_MAP["OPTIMO"] == "yellow"
    assert COLOR_MAP["SOBRE_MADURO"] == "red"


# ── postprocess: estado correcto para cada clase ──────────────────────────────
@pytest.mark.parametrize("class_id,fruit,state,color", [
    (0, "aguacate_hass", "INMADURO", "green"),
    (1, "aguacate_hass", "OPTIMO", "yellow"),
    (2, "aguacate_hass", "SOBRE_MADURO", "red"),
    (3, "platano", "INMADURO", "green"),
    (4, "platano", "OPTIMO", "yellow"),
    (5, "platano", "SOBRE_MADURO", "red"),
    (6, "tomate_usda", "INMADURO", "green"),
    (7, "tomate_usda", "OPTIMO", "yellow"),
    (8, "tomate_usda", "SOBRE_MADURO", "red"),
    (9, "mango", "INMADURO", "green"),
    (10, "mango", "OPTIMO", "yellow"),
    (11, "mango", "SOBRE_MADURO", "red"),
])
def test_postprocess_detecta_estado_correcto(class_id, fruit, state, color):
    res = svc.postprocess(_results(_FakeBox(conf=0.95, cls=class_id)))
    assert res is not None
    assert res.fruit_type == fruit
    assert res.maturity_label == state
    assert res.color_code == color
    assert res.recommendation == RECOMMENDATION_MAP[(fruit, state)]
    assert 0.0 <= res.confidence <= 1.0
    assert len(res.bbox) == 4


def test_postprocess_elige_la_deteccion_de_mayor_confianza():
    # Mismo frame con dos detecciones: debe ganar la de mayor confianza
    res = svc.postprocess(_results(
        _FakeBox(conf=0.60, cls=3),   # plátano INMADURO
        _FakeBox(conf=0.92, cls=10),  # mango OPTIMO  <- gana
    ))
    assert res.fruit_type == "mango"
    assert res.maturity_label == "OPTIMO"


def test_postprocess_bajo_umbral_devuelve_none():
    # Confianza por debajo del umbral (0.55) sin filtro -> sin estado
    res = svc.postprocess(_results(_FakeBox(conf=0.40, cls=4)))
    assert res is None


def test_postprocess_sin_detecciones_devuelve_none():
    assert svc.postprocess(_results()) is None
    assert svc.postprocess([_FakeResult(None)]) is None


# ── Filtro de fruta ───────────────────────────────────────────────────────────
def test_filtro_de_fruta_ignora_otras_frutas():
    # Pido 'mango' pero la detección fuerte es plátano -> no debe confundir estado
    res = svc.postprocess(
        _results(_FakeBox(conf=0.95, cls=4)),  # platano OPTIMO
        fruit_filter="mango",
    )
    assert res is None


def test_filtro_de_fruta_relaja_el_umbral():
    # Con filtro el umbral baja a la mitad (0.275): 0.40 ahora basta
    res = svc.postprocess(
        _results(_FakeBox(conf=0.40, cls=10)),
        fruit_filter="mango",
    )
    assert res is not None
    assert res.fruit_type == "mango"
    assert res.maturity_label == "OPTIMO"


def test_recomendacion_es_especifica_del_estado():
    inmaduro = svc.postprocess(_results(_FakeBox(0.9, 9)))   # mango INMADURO
    optimo = svc.postprocess(_results(_FakeBox(0.9, 10)))    # mango OPTIMO
    assert inmaduro.recommendation != optimo.recommendation
    assert "Madurar" in inmaduro.recommendation
