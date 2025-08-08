from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.src.infrastructure.adapters.driving.api import router as api_router
from app.config.logging_config import setup_logging
import logging

# Configurar logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação Car Sales")
    yield
    logger.info("Finalizando aplicação Car Sales")

app = FastAPI(
    title="Car Sales API",
    description="API para gerenciamento de vendas de carros",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api")