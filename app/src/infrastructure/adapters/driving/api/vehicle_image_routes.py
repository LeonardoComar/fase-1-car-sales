from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path
from typing import List
from app.src.application.services.vehicle_image_service import VehicleImageService
from app.src.application.dtos.vehicle_image_dto import (
    VehicleImagesResponse,
    ImageUploadResponse,
    ImageReorderRequest,
    SetPrimaryImageRequest
)
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.vehicle_image_repository_impl import VehicleImageRepositoryImpl
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_or_vendedor_user
)

router = APIRouter(prefix="/vehicles", tags=["Vehicle Images"])

def get_vehicle_image_service() -> VehicleImageService:
    """Dependency injection para o serviço de imagens"""
    vehicle_image_repository = VehicleImageRepositoryImpl()
    return VehicleImageService(vehicle_image_repository)

# Rotas para Carros
@router.post("/cars/{car_id}/images", response_model=List[ImageUploadResponse])
async def upload_car_images(
    car_id: int = Path(..., description="ID do carro"),
    files: List[UploadFile] = File(..., description="Imagens do carro (máximo 10)"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Upload de imagens para um carro.
    
    Requer autenticação: Administrador ou Vendedor
    
    Regras:
    - Máximo 10 imagens por carro
    - Mínimo 1 imagem por carro
    - Formatos aceitos: JPG, JPEG, PNG, WEBP
    - Tamanho máximo: 10MB por arquivo
    - Primeira imagem é definida como principal automaticamente
    """
    try:
        return image_service.upload_images("cars", car_id, files)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cars/{car_id}/images", response_model=VehicleImagesResponse)
async def get_car_images(
    car_id: int = Path(..., description="ID do carro"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Obter todas as imagens de um carro ordenadas por posição
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        return image_service.get_vehicle_images(car_id, "cars")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cars/{car_id}/images/{image_id}")
async def delete_car_image(
    car_id: int = Path(..., description="ID do carro"),
    image_id: int = Path(..., description="ID da imagem"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Deletar uma imagem de um carro.
    
    Requer autenticação: Administrador ou Vendedor
    
    Não é possível deletar se for a única imagem (mínimo 1).
    """
    try:
        success = image_service.delete_image(image_id)
        if success:
            return {"message": "Imagem deletada com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/cars/{car_id}/images/primary")
async def set_car_primary_image(
    request: SetPrimaryImageRequest,
    car_id: int = Path(..., description="ID do carro"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Definir uma imagem como principal para o carro
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        success = image_service.set_primary_image(car_id, request.image_id)
        if success:
            return {"message": "Imagem principal definida com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/cars/{car_id}/images/reorder")
async def reorder_car_images(
    request: ImageReorderRequest,
    car_id: int = Path(..., description="ID do carro"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Reordenar as imagens de um carro
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        success = image_service.reorder_images(car_id, request.image_positions)
        if success:
            return {"message": "Imagens reordenadas com sucesso"}
        else:
            raise HTTPException(status_code=400, detail="Erro ao reordenar imagens")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rotas para Motos
@router.post("/motorcycles/{motorcycle_id}/images", response_model=List[ImageUploadResponse])
async def upload_motorcycle_images(
    motorcycle_id: int = Path(..., description="ID da moto"),
    files: List[UploadFile] = File(..., description="Imagens da moto (máximo 10)"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Upload de imagens para uma moto.
    
    Requer autenticação: Administrador ou Vendedor
    
    Regras:
    - Máximo 10 imagens por moto
    - Mínimo 1 imagem por moto
    - Formatos aceitos: JPG, JPEG, PNG, WEBP
    - Tamanho máximo: 10MB por arquivo
    - Primeira imagem é definida como principal automaticamente
    """
    try:
        return image_service.upload_images("motorcycles", motorcycle_id, files)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/motorcycles/{motorcycle_id}/images", response_model=VehicleImagesResponse)
async def get_motorcycle_images(
    motorcycle_id: int = Path(..., description="ID da moto"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Obter todas as imagens de uma moto ordenadas por posição
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        return image_service.get_vehicle_images(motorcycle_id, "motorcycles")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/motorcycles/{motorcycle_id}/images/{image_id}")
async def delete_motorcycle_image(
    motorcycle_id: int = Path(..., description="ID da moto"),
    image_id: int = Path(..., description="ID da imagem"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Deletar uma imagem de uma moto.
    
    Requer autenticação: Administrador ou Vendedor
    
    Não é possível deletar se for a única imagem (mínimo 1).
    """
    try:
        success = image_service.delete_image(image_id)
        if success:
            return {"message": "Imagem deletada com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/motorcycles/{motorcycle_id}/images/primary")
async def set_motorcycle_primary_image(
    request: SetPrimaryImageRequest,
    motorcycle_id: int = Path(..., description="ID da moto"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Definir uma imagem como principal para a moto
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        success = image_service.set_primary_image(motorcycle_id, request.image_id)
        if success:
            return {"message": "Imagem principal definida com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/motorcycles/{motorcycle_id}/images/reorder")
async def reorder_motorcycle_images(
    request: ImageReorderRequest,
    motorcycle_id: int = Path(..., description="ID da moto"),
    image_service: VehicleImageService = Depends(get_vehicle_image_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Reordenar as imagens de uma moto
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        success = image_service.reorder_images(motorcycle_id, request.image_positions)
        if success:
            return {"message": "Imagens reordenadas com sucesso"}
        else:
            raise HTTPException(status_code=400, detail="Erro ao reordenar imagens")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
