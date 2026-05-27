class YOLO26Wrapper:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None

    def load_model(self, warmup: bool = True) -> None:
        import os
        from ultralytics import YOLO  # lazy import — not needed at module level

        self.model = YOLO(self.model_path)
        # Warmup solo en desarrollo: en produccion ahorra ~200MB de RAM
        # en el free tier de Render (512MB limite)
        if warmup and os.environ.get("ENVIRONMENT") != "production":
            self.warmup()

    def warmup(self):
        import numpy as np
        # Formato HWC (alto, ancho, canales) que espera Ultralytics
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, verbose=False)

    def predict(self, image, augment: bool = False) -> list:
        return self.model.predict(image, imgsz=640, verbose=False, augment=augment)