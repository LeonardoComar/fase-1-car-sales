from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.src.infrastructure.adapters.driving.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")