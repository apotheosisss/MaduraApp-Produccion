import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_all_tables
from app.core.yolo_wrapper import YOLO26Wrapper
from app.routers import auth, feedback, history, predict

# Ensure ORM models are registered with Base.metadata before create_all_tables
import app.models.scan_entity       # noqa: F401
import app.models.user_entity       # noqa: F401
import app.models.feedback_entity   # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "development":
        await create_all_tables()

    try:
        model = YOLO26Wrapper(settings.YOLO_MODEL_PATH)
        model.load_model()
        app.state.model = model
        logger.info("YOLO26n cargado correctamente desde %s", settings.YOLO_MODEL_PATH)
    except Exception as exc:
        logger.warning("No se pudo cargar el modelo YOLO: %s. Inferencia deshabilitada.", exc)
        app.state.model = None

    yield

    app.state.model = None


app = FastAPI(
    title="MaduraApp API",
    version="2.0.0",
    description="Backend de análisis de madurez agrícola con YOLO26n — con autenticación JWT y feedback",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/v1")
app.include_router(predict.router, prefix="/v1")
app.include_router(history.router, prefix="/v1")
app.include_router(feedback.router, prefix="/v1")


@app.get("/v1/health")
async def health() -> dict:
    return {
        "status": "ok",
        "model": "yolo26n",
        "version": "2.0.0",
        "model_loaded": app.state.model is not None,
    }
