from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.src.application.services.motorcycle_service import MotorcycleService
from app.src.application.dtos.motorcycle_dto import CreateMotorcycleRequest, MotorcycleResponse
from app.src.infrastructure.driven.persistence.motorcycle_repository_impl import MotorcycleRepository
import logging

logger = logging.getLogger(__name__)

# Criar instâncias dos serviços
motorcycle_repository = MotorcycleRepository()
motorcycle_service = MotorcycleService(motorcycle_repository)

router = APIRouter(prefix="/motorcycles", tags=["Motorcycles"])


def get_motorcycle_service() -> MotorcycleService:
    """
    Dependency injection para o serviço de motos.
    """
    return motorcycle_service


@router.post("/", response_model=MotorcycleResponse, status_code=status.HTTP_201_CREATED)
async def create_motorcycle(
    request: CreateMotorcycleRequest,
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcycleResponse:
    """
    Cria uma nova moto.
    
    Args:
        request: Dados da moto a ser criada
        service: Serviço de motos (injetado)
        
    Returns:
        MotorcycleResponse: Dados da moto criada
        
    Raises:
        HTTPException: 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para criar moto: {request.model}")
        
        motorcycle_response = await service.create_motorcycle(request)
        
        logger.info(f"Moto criada com sucesso via API. ID: {motorcycle_response.id}")
        return motorcycle_response
        
    except ValueError as e:
        logger.warning(f"Dados inválidos para criação de moto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao criar moto via API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/list-motorcycles-ordered-by-price", response_model=List[MotorcycleResponse])
async def get_active_motorcycles_ordered_by_price(
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> List[MotorcycleResponse]:
    """
    Lista todas as motos com status 'Ativo' ordenadas por preço (menor para maior).
    
    Args:
        service: Serviço de motos (injetado)
        
    Returns:
        List[MotorcycleResponse]: Lista de motos ativas ordenadas por preço
        
    Raises:
        HTTPException: 500 se erro interno
    """
    try:
        logger.info("Recebida requisição para listar motos ativas ordenadas por preço")
        
        motorcycles = await service.get_active_motorcycles_by_price()
        
        logger.info(f"Encontradas {len(motorcycles)} motos ativas ordenadas por preço")
        return motorcycles
        
    except Exception as e:
        logger.error(f"Erro interno ao listar motos ativas ordenadas por preço via API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{motorcycle_id}", response_model=MotorcycleResponse)
async def get_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcycleResponse:
    """
    Busca uma moto pelo ID.
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        
    Returns:
        MotorcycleResponse: Dados da moto encontrada
        
    Raises:
        HTTPException: 404 se não encontrada, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para buscar moto ID: {motorcycle_id}")
        
        motorcycle_response = await service.get_motorcycle_by_id(motorcycle_id)
        if not motorcycle_response:
            logger.info(f"Moto não encontrada via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto encontrada via API. ID: {motorcycle_id}")
        return motorcycle_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao buscar moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{motorcycle_id}", response_model=MotorcycleResponse)
async def update_motorcycle(
    motorcycle_id: int,
    request: CreateMotorcycleRequest,
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcycleResponse:
    """
    Atualiza uma moto existente.
    
    Args:
        motorcycle_id: ID da moto
        request: Novos dados da moto
        service: Serviço de motos (injetado)
        
    Returns:
        MotorcycleResponse: Dados da moto atualizada
        
    Raises:
        HTTPException: 404 se não encontrada, 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para atualizar moto ID: {motorcycle_id}")
        
        motorcycle_response = await service.update_motorcycle(motorcycle_id, request)
        if not motorcycle_response:
            logger.info(f"Moto não encontrada para atualização via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto atualizada com sucesso via API. ID: {motorcycle_id}")
        return motorcycle_response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Dados inválidos para atualização de moto ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao atualizar moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{motorcycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service)
):
    """
    Remove uma moto.
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        
    Raises:
        HTTPException: 404 se não encontrada, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para remover moto ID: {motorcycle_id}")
        
        result = await service.delete_motorcycle(motorcycle_id)
        if not result:
            logger.info(f"Moto não encontrada para remoção via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto removida com sucesso via API. ID: {motorcycle_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao remover moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{motorcycle_id}/inactive", response_model=MotorcycleResponse)
async def inactivate_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcycleResponse:
    """
    Inativa uma moto alterando seu status para 'Inativo'.
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        
    Returns:
        MotorcycleResponse: Dados da moto inativada
        
    Raises:
        HTTPException: 404 se não encontrada, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para inativar moto ID: {motorcycle_id}")
        
        motorcycle_response = await service.inactivate_motorcycle(motorcycle_id)
        if not motorcycle_response:
            logger.info(f"Moto não encontrada para inativação via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto inativada com sucesso via API. ID: {motorcycle_id}")
        return motorcycle_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao inativar moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{motorcycle_id}/active", response_model=MotorcycleResponse)
async def activate_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcycleResponse:
    """
    Ativa uma moto alterando seu status para 'Ativo'.
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        
    Returns:
        MotorcycleResponse: Dados da moto ativada
        
    Raises:
        HTTPException: 404 se não encontrada, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para ativar moto ID: {motorcycle_id}")
        
        motorcycle_response = await service.activate_motorcycle(motorcycle_id)
        if not motorcycle_response:
            logger.info(f"Moto não encontrada para ativação via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto ativada com sucesso via API. ID: {motorcycle_id}")
        return motorcycle_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao ativar moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
