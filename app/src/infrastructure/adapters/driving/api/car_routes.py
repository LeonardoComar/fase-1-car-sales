from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.src.application.services.car_service import CarService
from app.src.application.dtos.car_dto import CreateCarRequest, CarResponse
from app.src.infrastructure.driven.persistence.car_repository_impl import CarRepository
import logging

logger = logging.getLogger(__name__)

# Criar instâncias dos serviços
car_repository = CarRepository()
car_service = CarService(car_repository)

router = APIRouter(prefix="/cars", tags=["Cars"])


def get_car_service() -> CarService:
    """
    Dependency injection para o serviço de carros.
    """
    return car_service


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    request: CreateCarRequest,
    service: CarService = Depends(get_car_service)
) -> CarResponse:
    """
    Cria um novo carro.
    
    Args:
        request: Dados do carro a ser criado
        service: Serviço de carros (injetado)
        
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


@router.get("/list-cars-ordered-by-price", response_model=List[CarResponse])
async def get_active_cars_ordered_by_price(
    service: CarService = Depends(get_car_service)
) -> List[CarResponse]:
    """
    Lista todos os carros com status 'Ativo' ordenados por preço (menor para maior).
    
    Args:
        service: Serviço de carros (injetado)
        
    Returns:
        List[CarResponse]: Lista de carros ativos ordenados por preço
        
    Raises:
        HTTPException: 500 se erro interno
    """
    try:
        logger.info("Recebida requisição para listar carros ativos ordenados por preço")
        
        cars = await service.get_active_cars_by_price()
        
        logger.info(f"Encontrados {len(cars)} carros ativos ordenados por preço")
        return cars
        
    except Exception as e:
        logger.error(f"Erro interno ao listar carros ativos ordenados por preço via API: {str(e)}")
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
    service: CarService = Depends(get_car_service)
) -> CarResponse:
    """
    Atualiza um carro existente.
    
    Args:
        car_id: ID do carro
        request: Novos dados do carro
        service: Serviço de carros (injetado)
        
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
    service: CarService = Depends(get_car_service)
):
    """
    Remove um carro.
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        
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


@router.patch("/{car_id}/inactive", response_model=CarResponse)
async def inactivate_car(
    car_id: int,
    service: CarService = Depends(get_car_service)
) -> CarResponse:
    """
    Inativa um carro alterando seu status para 'Inativo'.
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        
    Returns:
        CarResponse: Dados do carro inativado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para inativar carro ID: {car_id}")
        
        car_response = await service.inactivate_car(car_id)
        if not car_response:
            logger.info(f"Carro não encontrado para inativação via API. ID: {car_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carro não encontrado"
            )
        
        logger.info(f"Carro inativado com sucesso via API. ID: {car_id}")
        return car_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao inativar carro via API. ID {car_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{car_id}/active", response_model=CarResponse)
async def activate_car(
    car_id: int,
    service: CarService = Depends(get_car_service)
) -> CarResponse:
    """
    Ativa um carro alterando seu status para 'Ativo'.
    
    Args:
        car_id: ID do carro
        service: Serviço de carros (injetado)
        
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
