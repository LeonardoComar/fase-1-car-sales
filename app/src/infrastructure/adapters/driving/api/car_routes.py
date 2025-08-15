from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.src.application.services.car_service import CarService
from app.src.application.dtos.car_dto import CreateCarRequest, CarResponse, CarsListResponse
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.car_repository_impl import CarRepository
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_or_vendedor_user
)
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cars", tags=["Cars"])


def get_car_service() -> CarService:
    """
    Dependency injection para o serviço de carros.
    """
    car_repository = CarRepository()
    car_service = CarService(car_repository)
    return car_service


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    request: CreateCarRequest,
    service: CarService = Depends(get_car_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> CarResponse:
    """
    Cria um novo carro.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        request: Dados do carro a ser criado
        service: Serviço de carros (injetado)
        current_user: Usuário autenticado
        
    Returns:
        CarResponse: Dados do carro criado
        
    Raises:
        HTTPException: 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para criar carro: {request.model}")
        
        car_response = await service.create_car(request)
        
        logger.info(f"Carro criado com sucesso via API. ID: {car_response.id}")
        return car_response
        
    except ValueError as e:
        logger.warning(f"Dados inválidos para criação de carro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao criar carro via API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/", response_model=CarsListResponse)
async def get_cars(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros para retornar"),
    order_by_price: Optional[str] = Query(None, regex="^(asc|desc)$", description="Ordenação por preço: 'asc' ou 'desc'"),
    status: Optional[str] = Query(None, description="Status dos carros para filtrar"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Preço mínimo para filtrar"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Preço máximo para filtrar"),
    service: CarService = Depends(get_car_service)
) -> CarsListResponse:
    """
    Lista carros com filtros opcionais.
    
    Args:
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        order_by_price: Ordenação por preço - 'asc' crescente ou 'desc' decrescente
        status: Status dos carros para filtrar (ex: 'Ativo', 'Inativo')
        min_price: Preço mínimo para filtrar
        max_price: Preço máximo para filtrar
        service: Serviço de carros (injetado)
        
    Returns:
        CarsListResponse: Lista de carros com metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para listar carros. Filtros: order_by_price={order_by_price}, status={status}, min_price={min_price}, max_price={max_price}")
        
        # Validação do range de preços
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço mínimo não pode ser maior que o preço máximo"
            )
        
        cars_response = await service.get_cars_with_filters(
            skip=skip,
            limit=limit,
            order_by_price=order_by_price,
            status=status,
            min_price=min_price,
            max_price=max_price
        )
        
        logger.info(f"Encontrados {cars_response.total} carros com os filtros aplicados")
        return cars_response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao listar carros: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro interno ao listar carros via API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: int,
    service: CarService = Depends(get_car_service)
) -> CarResponse:
    """
    Busca um carro pelo ID.
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        
    Returns:
        CarResponse: Dados do carro encontrado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para buscar carro ID: {car_id}")
        
        car_response = await service.get_car_by_id(car_id)
        if not car_response:
            logger.info(f"Carro não encontrado via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro encontrado via API. ID: {car_id}")
        return car_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao buscar carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    request: CreateCarRequest,
    service: CarService = Depends(get_car_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> CarResponse:
    """
    Atualiza um carro existente.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        car_id: ID do carro
        request: Novos dados do carro
        service: Serviço de carros (injetado)
        current_user: Usuário autenticado
        
    Returns:
        CarResponse: Dados do carro atualizado
        
    Raises:
        HTTPException: 404 se não encontrado, 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para atualizar carro ID: {car_id}")
        
        car_response = await service.update_car(car_id, request)
        if not car_response:
            logger.info(f"Carro não encontrado para atualização via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro atualizado com sucesso via API. ID: {car_id}")
        return car_response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Dados inválidos para atualização de carro ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao atualizar carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    service: CarService = Depends(get_car_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Remove um carro.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        current_user: Usuário autenticado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para remover carro ID: {car_id}")
        
        result = await service.delete_car(car_id)
        if not result:
            logger.info(f"Carro não encontrado para remoção via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro removido com sucesso via API. ID: {car_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao remover carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{car_id}/deactivate", response_model=CarResponse)
async def deactivate_car(
    car_id: int,
    service: CarService = Depends(get_car_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> CarResponse:
    """
    Desativa um carro alterando seu status para 'Inativo'.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        current_user: Usuário autenticado
        
    Returns:
        CarResponse: Dados do carro desativado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para desativar carro ID: {car_id}")
        
        car_response = await service.inactivate_car(car_id)
        if not car_response:
            logger.info(f"Carro não encontrado para desativação via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro desativado com sucesso via API. ID: {car_id}")
        return car_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao desativar carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{car_id}/activate", response_model=CarResponse)
async def activate_car(
    car_id: int,
    service: CarService = Depends(get_car_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> CarResponse:
    """
    Ativa um carro alterando seu status para 'Ativo'.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        current_user: Usuário autenticado
        
    Returns:
        CarResponse: Dados do carro ativado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para ativar carro ID: {car_id}")
        
        car_response = await service.activate_car(car_id)
        if not car_response:
            logger.info(f"Carro não encontrado para ativação via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro ativado com sucesso via API. ID: {car_id}")
        return car_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao ativar carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
