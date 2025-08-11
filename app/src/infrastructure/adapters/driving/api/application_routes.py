from fastapi import APIRouter
from app.src.infrastructure.adapters.driving.api.car_routes import router as car_router
from app.src.infrastructure.adapters.driving.api.motorcycle_routes import router as motorcycle_router
from app.src.infrastructure.adapters.driving.api.client_routes import router as client_router

router = APIRouter()

# Incluir as rotas de carros
router.include_router(car_router)

# Incluir as rotas de motos
router.include_router(motorcycle_router)

# Incluir as rotas de clientes
router.include_router(client_router)

# Rota de Health Check
@router.get("/health_check")
async def health_check():
    return {"status": "ok"}