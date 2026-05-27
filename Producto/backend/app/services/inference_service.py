import gc
import io

import numpy as np
from PIL import Image, ImageFile

# Permitir cargar JPEGs ligeramente truncados (descargas incompletas, etc.)
ImageFile.LOAD_TRUNCATED_IMAGES = True

from app.core.config import settings
from app.schemas.scan_result import ScanResult

CLASS_MAP: dict[int, tuple[str, str]] = {
    0: ("aguacate_hass", "INMADURO"),
    1: ("aguacate_hass", "OPTIMO"),
    2: ("aguacate_hass", "SOBRE_MADURO"),
    3: ("platano", "INMADURO"),
    4: ("platano", "OPTIMO"),
    5: ("platano", "SOBRE_MADURO"),
    6: ("tomate_usda", "INMADURO"),
    7: ("tomate_usda", "OPTIMO"),
    8: ("tomate_usda", "SOBRE_MADURO"),
    9: ("mango", "INMADURO"),
    10: ("mango", "OPTIMO"),
    11: ("mango", "SOBRE_MADURO"),
}

COLOR_MAP: dict[str, str] = {
    "INMADURO": "green",
    "OPTIMO": "yellow",
    "SOBRE_MADURO": "red",
}

RECOMMENDATION_MAP: dict[tuple[str, str], str] = {
    # Aguacate Hass — madura post-cosecha, etileno acelera proceso
    ("aguacate_hass", "INMADURO"):
        "Madurar 4-7 días a temperatura ambiente. Acelera colocándolo en "
        "bolsa de papel junto a un plátano.",
    ("aguacate_hass", "OPTIMO"):
        "Listo para consumir. Refrigera hasta 2 días para retrasar maduración.",
    ("aguacate_hass", "SOBRE_MADURO"):
        "Consumir hoy — ideal para guacamole, untar en tostadas o batidos.",

    # Plátano — el más sensible al etileno, madura rápido
    ("platano", "INMADURO"):
        "Madurar 2-4 días a temperatura ambiente. Bolsa de papel cerrada acelera.",
    ("platano", "OPTIMO"):
        "Punto ideal de consumo. Refrigera (la piel se oscurece pero la pulpa "
        "se mantiene) para extender 2-3 días más.",
    ("platano", "SOBRE_MADURO"):
        "Pulpa muy dulce — perfecto para batidos, pan de plátano, panqueques.",

    # Tomate cherry — madura más lento que los grandes
    ("tomate_usda", "INMADURO"):
        "Madurar 7-14 días a temperatura ambiente (nunca refrigerar verde). "
        "Junto a una manzana o plátano se acelera 3-4 días.",
    ("tomate_usda", "OPTIMO"):
        "Sabor óptimo. Consumir en 2-3 días. No refrigerar para conservar "
        "aroma y textura.",
    ("tomate_usda", "SOBRE_MADURO"):
        "Ideal para salsas, sofritos o gazpacho. Consumir hoy.",

    # Mango — climatérico clásico, suaviza al madurar
    ("mango", "INMADURO"):
        "Madurar 4-7 días a temperatura ambiente. Envolver en papel periódico "
        "acelera 2 días.",
    ("mango", "OPTIMO"):
        "Listo para consumir — cede ligeramente al presionar y huele dulce "
        "cerca del tallo.",
    ("mango", "SOBRE_MADURO"):
        "Pulpa muy blanda — perfecto para batidos, jugos, helados o chutneys.",
}

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


class InferenceService:
    def validate_image(self, image_bytes: bytes) -> bool:
        if len(image_bytes) > MAX_IMAGE_BYTES:
            return False
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            return True
        except Exception:
            return False

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        # Abrir, reducir a 640x640 y liberar inmediatamente el objeto PIL
        # para minimizar el pico de RAM durante inferencia en free tier
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert("RGB").resize((640, 640), Image.LANCZOS)
            return np.array(img)

    def postprocess(
        self,
        results: list,
        fruit_filter: str | None = None,
    ) -> ScanResult | None:
        # Si hay filtro, el threshold se relaja porque acotamos las clases
        threshold = (
            settings.CONFIDENCE_THRESHOLD * 0.5
            if fruit_filter
            else settings.CONFIDENCE_THRESHOLD
        )

        best_box = None
        best_conf = threshold
        best_class_id = -1

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
            for box in result.boxes:
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                if class_id not in CLASS_MAP:
                    continue
                if fruit_filter and CLASS_MAP[class_id][0] != fruit_filter:
                    continue
                if conf >= best_conf:
                    best_conf = conf
                    best_box = box
                    best_class_id = class_id

        if best_box is None:
            return None

        fruit_type, maturity_label = CLASS_MAP[best_class_id]
        bbox = [round(v, 2) for v in best_box.xyxy[0].tolist()]

        return ScanResult(
            fruit_type=fruit_type,
            maturity_label=maturity_label,
            confidence=round(best_conf, 4),
            bbox=bbox,
            recommendation=RECOMMENDATION_MAP[(fruit_type, maturity_label)],
            color_code=COLOR_MAP[maturity_label],
        )

    def run(
        self,
        image_bytes: bytes,
        model,
        fruit_filter: str | None = None,
    ) -> ScanResult | None:
        image_array = self.preprocess(image_bytes)
        # TTA solo cuando hay filtro: ya sabemos qué fruta es, vale la pena
        # gastar el 2x de tiempo de inferencia a cambio de +2-3% de precisión
        results = model.predict(image_array, augment=fruit_filter is not None)
        scan_result = self.postprocess(results, fruit_filter)
        del results, image_array
        gc.collect()
        return scan_result
