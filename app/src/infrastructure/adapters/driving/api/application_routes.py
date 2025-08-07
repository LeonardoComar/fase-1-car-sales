from fastapi import APIRouter

router = APIRouter()

# Rota de Health Check
@router.get("/health_check")
async def health_check():
    return {"status": "ok"}