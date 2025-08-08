from fastapi import APIRouter
from app.src.infrastructure.adapters.driving.api.car_routes import router as car_router

router = APIRouter()

# Incluir as rotas de carros
router.include_router(car_router)

# Rota de Health Check
@router.get("/health_check")
async def health_check():
    return {"status": "ok"}