from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.src.infrastructure.adapters.driving.api import router as api_router
from app.config.logging_config import setup_logging
import logging

# Configurar logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação Car Sales")
    
    # Criar diretórios de upload se não existirem
    static_dir = Path("static/uploads")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar diretório de thumbnails
    thumbnail_dir = Path("static/uploads/thumbnails")
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    logger.info("Finalizando aplicação Car Sales")

app = FastAPI(
    title="Car Sales API",
    description="API para gerenciamento de vendas de carros",
    version="1.0.0",
    lifespan=lifespan
)

# Criar diretório static se não existir (antes de montar)
static_path = Path("static")
static_path.mkdir(parents=True, exist_ok=True)

# Montar arquivos estáticos para servir imagens
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")