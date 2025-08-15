from fastapi import APIRouter
from app.src.infrastructure.adapters.driving.api.car_routes import router as car_router
from app.src.infrastructure.adapters.driving.api.motorcycle_routes import router as motorcycle_router
from app.src.infrastructure.adapters.driving.api.client_routes import router as client_router
from app.src.infrastructure.adapters.driving.api.employee_routes import router as employee_router
from app.src.infrastructure.adapters.driving.api.sale_routes import router as sale_router
from app.src.infrastructure.adapters.driving.api.message_routes import router as message_router
from app.src.infrastructure.adapters.driving.api.vehicle_image_routes import router as vehicle_image_router
from app.src.infrastructure.adapters.driving.api.auth_routes import auth_router, users_router

router = APIRouter()

# Incluir as rotas de autenticação
router.include_router(auth_router)
router.include_router(users_router)

# Incluir as rotas de carros
router.include_router(car_router)

# Incluir as rotas de motos
router.include_router(motorcycle_router)

# Incluir as rotas de clientes
router.include_router(client_router)

# Incluir as rotas de funcionários
router.include_router(employee_router)

# Incluir as rotas de vendas
router.include_router(sale_router)

# Incluir as rotas de mensagens
router.include_router(message_router)

# Incluir as rotas de imagens de veículos
router.include_router(vehicle_image_router)
router.include_router(vehicle_image_router)

# Rota de Health Check
@router.get("/health_check")
async def health_check():
    return {"status": "ok"}