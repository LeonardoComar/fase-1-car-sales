from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.src.infrastructure.adapters.driving.api import router as api_router
from app.src.infrastructure.startup.system_initializer import initialize_system
from app.config.logging_config import setup_logging
import logging

# Configurar logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicação Car Sales")
    
    # Criar diretórios de upload se não existirem
    static_dir = Path("static/uploads")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar diretório de thumbnails
    thumbnail_dir = Path("static/uploads/thumbnails")
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar sistema automaticamente (criar usuário admin, etc.)
    await initialize_system()
    
    yield
    logger.info("🔄 Finalizando aplicação Car Sales")

app = FastAPI(
    title="🚗 Car Sales API",
    description="""
    ## Sistema Completo de Vendas de Veículos
    
    API RESTful para gerenciamento de vendas de carros e motocicletas com arquitetura hexagonal.
    
    ### ✨ Principais Funcionalidades:
    
    * **� Autenticação**: Sistema JWT com controle de acesso por perfis (Administrador/Vendedor)
    * **�🚗 Veículos**: CRUD completo para carros e motocicletas
    * **📸 Imagens**: Upload, gerenciamento e organização de imagens dos veículos
    * **👥 Clientes**: Gestão completa de clientes
    * **👨‍💼 Funcionários**: Controle de colaboradores
    * **💰 Vendas**: Registro e acompanhamento de vendas
    * **💬 Mensagens**: Sistema de comunicação e atendimento com autenticação
    * **🔍 Filtros**: Busca avançada com múltiplos critérios
    
    ### 🔑 Autenticação:
    1. **Usuário Administrador Automático**: `admin@carsales.com` / `admin123456` (criado automaticamente no startup)
    2. **Login**: Faça login em `/api/auth/login` para obter um token JWT
    3. **Logout**: Use `/api/auth/logout` para invalidar o token atual
    4. **Autorização**: Use o token no header: `Authorization: Bearer <seu-token>`
    5. **Perfis**: **Administrador** (acesso total, sem funcionário) e **Vendedor** (operações de vendas, com funcionário associado)
    
    ### 📖 Como usar:
    1. **Início Rápido**: A aplicação cria automaticamente o usuário administrador na primeira execução
    2. Faça login com as credenciais padrão para obter token de autenticação
    3. ⚠️ **IMPORTANTE**: Altere a senha padrão em produção!
    4. Explore os endpoints abaixo
    5. Use as collections do Postman na pasta `Postman/`
    6. Consulte a documentação completa na pasta `Documentação/`
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