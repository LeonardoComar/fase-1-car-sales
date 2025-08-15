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
    title="🚗 Car Sales API",
    description="""
    ## Sistema Completo de Vendas de Veículos
    
    API RESTful para gerenciamento de vendas de carros e motocicletas com arquitetura hexagonal.
    
    ### ✨ Principais Funcionalidades:
    
    * **🚗 Veículos**: CRUD completo para carros e motocicletas
    * **📸 Imagens**: Upload, gerenciamento e organização de imagens dos veículos
    * **👥 Clientes**: Gestão completa de clientes
    * **👨‍💼 Funcionários**: Controle de colaboradores
    * **💰 Vendas**: Registro e acompanhamento de vendas
    * **💬 Mensagens**: Sistema de comunicação e atendimento
    * **🔍 Filtros**: Busca avançada com múltiplos critérios
    
    ### 📖 Como usar:
    1. Explore os endpoints abaixo
    2. Use as collections do Postman na pasta `Postman/`
    3. Consulte a documentação completa na pasta `Documentação/`
    """,
    version="1.0.0",
    contact={
        "name": "Leonardo Comar",
        "url": "https://github.com/LeonardoComar",
        "email": "leonardo.comar@exemplo.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Criar diretório static se não existir (antes de montar)
static_path = Path("static")
static_path.mkdir(parents=True, exist_ok=True)

# Montar arquivos estáticos para servir imagens
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")