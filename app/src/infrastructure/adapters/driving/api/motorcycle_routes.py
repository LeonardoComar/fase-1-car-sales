from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.src.application.services.motorcycle_service import MotorcycleService
from app.src.application.dtos.motorcycle_dto import CreateMotorcycleRequest, MotorcycleResponse, MotorcyclesListResponse
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.motorcycle_repository_impl import MotorcycleRepository
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_or_vendedor_user
)
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/motorcycles", tags=["Motorcycles"])


def get_motorcycle_service() -> MotorcycleService:
    """
    Dependency injection para o serviço de motos.
    """
    motorcycle_repository = MotorcycleRepository()
    motorcycle_service = MotorcycleService(motorcycle_repository)
    return motorcycle_service


@router.post("/", response_model=MotorcycleResponse, status_code=status.HTTP_201_CREATED)
async def create_motorcycle(
    request: CreateMotorcycleRequest,
    service: MotorcycleService = Depends(get_motorcycle_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> MotorcycleResponse:
    """
    Cria uma nova moto.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        request: Dados da moto a ser criada
        service: Serviço de motos (injetado)
        current_user: Usuário autenticado
        
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


@router.get("/", response_model=MotorcyclesListResponse)
async def get_motorcycles(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros para retornar"),
    order_by_price: Optional[str] = Query(None, regex="^(asc|desc)$", description="Ordenação por preço: 'asc' ou 'desc'"),
    status: Optional[str] = Query(None, description="Status das motocicletas para filtrar"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Preço mínimo para filtrar"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Preço máximo para filtrar"),
    service: MotorcycleService = Depends(get_motorcycle_service)
) -> MotorcyclesListResponse:
    """
    Lista motocicletas com filtros opcionais.
    
    Args:
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        order_by_price: Ordenação por preço - 'asc' crescente ou 'desc' decrescente
        status: Status das motocicletas para filtrar (ex: 'Ativo', 'Inativo')
        min_price: Preço mínimo para filtrar
        max_price: Preço máximo para filtrar
        service: Serviço de motocicletas (injetado)
        
    Returns:
        MotorcyclesListResponse: Lista de motocicletas com metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para listar motocicletas. Filtros: order_by_price={order_by_price}, status={status}, min_price={min_price}, max_price={max_price}")
        
        # Validação do range de preços
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço mínimo não pode ser maior que o preço máximo"
            )
        
        motorcycles_response = await service.get_motorcycles_with_filters(
            skip=skip,
            limit=limit,
            order_by_price=order_by_price,
            status=status,
            min_price=min_price,
            max_price=max_price
        )
        
        logger.info(f"Encontradas {motorcycles_response.total} motocicletas com os filtros aplicados")
        return motorcycles_response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao listar motocicletas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro interno ao listar motocicletas via API: {str(e)}")
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
    service: MotorcycleService = Depends(get_motorcycle_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> MotorcycleResponse:
    """
    Atualiza uma moto existente.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        motorcycle_id: ID da moto
        request: Novos dados da moto
        service: Serviço de motos (injetado)
        current_user: Usuário autenticado
        
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
    service: MotorcycleService = Depends(get_motorcycle_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Remove uma moto.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        current_user: Usuário autenticado
        
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


@router.patch("/{motorcycle_id}/deactivate", response_model=MotorcycleResponse)
async def deactivate_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> MotorcycleResponse:
    """
    Desativa uma moto alterando seu status para 'Inativo'.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        current_user: Usuário autenticado
        
    Returns:
        MotorcycleResponse: Dados da moto desativada
        
    Raises:
        HTTPException: 404 se não encontrada, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para desativar moto ID: {motorcycle_id}")
        
        motorcycle_response = await service.inactivate_motorcycle(motorcycle_id)
        if not motorcycle_response:
            logger.info(f"Moto não encontrada para desativação via API. ID: {motorcycle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto não encontrada"
            )
        
        logger.info(f"Moto desativada com sucesso via API. ID: {motorcycle_id}")
        return motorcycle_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao desativar moto via API. ID {motorcycle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{motorcycle_id}/activate", response_model=MotorcycleResponse)
async def activate_motorcycle(
    motorcycle_id: int,
    service: MotorcycleService = Depends(get_motorcycle_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> MotorcycleResponse:
    """
    Ativa uma moto alterando seu status para 'Ativo'.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        motorcycle_id: ID da moto
        service: Serviço de motos (injetado)
        current_user: Usuário autenticado
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
