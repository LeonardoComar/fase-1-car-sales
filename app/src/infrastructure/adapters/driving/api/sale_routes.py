from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from app.src.application.services.sale_service import SaleService
from app.src.application.dtos.sale_dto import (
    CreateSaleRequest, UpdateSaleRequest, UpdateSaleStatusRequest,
    SaleResponse, SaleListResponse, SalesListResponse
)
from app.src.infrastructure.driven.persistence.sale_repository_impl import SaleRepositoryImpl
from app.src.infrastructure.driven.persistence.car_repository_impl import CarRepository
from app.src.infrastructure.driven.persistence.motorcycle_repository_impl import MotorcycleRepository
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Router para as rotas de vendas
router = APIRouter(prefix="/sales", tags=["Sales"])


def get_sale_service() -> SaleService:
    """
    Dependency injection para o serviço de vendas.
    
    Returns:
        SaleService: Instância do serviço de vendas
    """
    sale_repository = SaleRepositoryImpl()
    car_repository = CarRepository()
    motorcycle_repository = MotorcycleRepository()
    return SaleService(sale_repository, car_repository, motorcycle_repository)


@router.post("/", response_model=SaleResponse, status_code=201)
async def create_sale(
    request: CreateSaleRequest,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Cria uma nova venda.
    
    Args:
        request: Dados da venda a ser criada
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda criada
        
    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        logger.info("Recebida solicitação para criar venda")
        sale = await sale_service.create_sale(request)
        logger.info(f"Venda criada com sucesso. ID: {sale.id}")
        return sale
        
    except ValueError as e:
        logger.error(f"Erro de validação ao criar venda: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao criar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", response_model=SalesListResponse)
async def get_sales(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros para retornar"),
    client_id: Optional[int] = Query(None, description="ID do cliente"),
    employee_id: Optional[int] = Query(None, description="ID do funcionário"),
    status: Optional[str] = Query(None, description="Status da venda"),
    payment_method: Optional[str] = Query(None, description="Forma de pagamento"),
    start_date: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    order_by_value: Optional[str] = Query(None, description="Ordenar por valor: 'asc' (crescente) ou 'desc' (decrescente)"),
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Lista vendas com filtros unificados.
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros para retornar
        client_id: ID do cliente (opcional)
        employee_id: ID do funcionário (opcional)
        status: Status das vendas (opcional)
        payment_method: Forma de pagamento (opcional)
        start_date: Data inicial (opcional)
        end_date: Data final (opcional)
        order_by_value: Ordenação por valor - 'asc' para crescente, 'desc' para decrescente (opcional)
        sale_service: Serviço de vendas
        
    Returns:
        SalesListResponse: Lista de vendas
        
    Raises:
        HTTPException: Se houver erro na busca
    """
    try:
        logger.info("Recebida solicitação para listar vendas")
        
        # Validar parâmetro de ordenação
        if order_by_value and order_by_value not in ['asc', 'desc']:
            raise HTTPException(status_code=400, detail="order_by_value deve ser 'asc' ou 'desc'")
        
        sales = await sale_service.get_sales_with_filters(
            skip=skip, limit=limit,
            client_id=client_id, employee_id=employee_id,
            status=status, payment_method=payment_method,
            start_date=start_date, end_date=end_date,
            order_by_value=order_by_value
        )
        
        logger.info(f"Listagem de vendas realizada com sucesso. Total: {len(sales)}")
        return SalesListResponse(sales=sales, total=len(sales))
        
    except Exception as e:
        logger.error(f"Erro inesperado ao listar vendas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale_by_id(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Busca uma venda pelo ID.
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para buscar venda. ID: {sale_id}")
        
        sale = await sale_service.get_sale_by_id(sale_id)
        
        if not sale:
            logger.warning(f"Venda não encontrada. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda encontrada com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int,
    request: UpdateSaleRequest,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Atualiza uma venda existente.
    
    Args:
        sale_id: ID da venda
        request: Dados para atualização
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda atualizada
        
    Raises:
        HTTPException: Se a venda não for encontrada ou houver erro de validação
    """
    try:
        logger.info(f"Recebida solicitação para atualizar venda. ID: {sale_id}")
        
        sale = await sale_service.update_sale(sale_id, request)
        
        if not sale:
            logger.warning(f"Venda não encontrada para atualização. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda atualizada com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar venda {sale_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/status", response_model=SaleResponse)
async def update_sale_status(
    sale_id: int,
    request: UpdateSaleStatusRequest,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Atualiza apenas o status de uma venda.
    
    Args:
        sale_id: ID da venda
        request: Novo status
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda atualizada
        
    Raises:
        HTTPException: Se a venda não for encontrada ou status for inválido
    """
    try:
        logger.info(f"Recebida solicitação para atualizar status da venda. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, request.status)
        
        if not sale:
            logger.warning(f"Venda não encontrada para atualização de status. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Status da venda atualizado com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar status da venda {sale_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar status da venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/confirm", response_model=SaleResponse)
async def confirm_sale(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Confirma uma venda (altera status para "Confirmada").
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda confirmada
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para confirmar venda. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, "Confirmada")
        
        if not sale:
            logger.warning(f"Venda não encontrada para confirmação. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda confirmada com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao confirmar venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/pay", response_model=SaleResponse)
async def mark_sale_as_paid(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Marca uma venda como paga (altera status para "Paga").
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda marcada como paga
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para marcar venda como paga. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, "Paga")
        
        if not sale:
            logger.warning(f"Venda não encontrada para marcar como paga. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda marcada como paga com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao marcar venda como paga {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/deliver", response_model=SaleResponse)
async def mark_sale_as_delivered(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Marca uma venda como entregue (altera status para "Entregue").
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda marcada como entregue
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para marcar venda como entregue. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, "Entregue")
        
        if not sale:
            logger.warning(f"Venda não encontrada para marcar como entregue. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda marcada como entregue com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao marcar venda como entregue {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/cancel", response_model=SaleResponse)
async def cancel_sale(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Cancela uma venda (altera status para "Cancelada").
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda cancelada
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para cancelar venda. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, "Cancelada")
        
        if not sale:
            logger.warning(f"Venda não encontrada para cancelamento. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda cancelada com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao cancelar venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{sale_id}/pending", response_model=SaleResponse)
async def mark_sale_as_pending(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Marca uma venda como pendente (altera status para "Pendente").
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Returns:
        SaleResponse: Dados da venda marcada como pendente
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para marcar venda como pendente. ID: {sale_id}")
        
        sale = await sale_service.update_sale_status(sale_id, "Pendente")
        
        if not sale:
            logger.warning(f"Venda não encontrada para marcar como pendente. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda marcada como pendente com sucesso. ID: {sale_id}")
        return sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao marcar venda como pendente {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{sale_id}", status_code=204)
async def delete_sale(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Remove uma venda.
    
    Args:
        sale_id: ID da venda
        sale_service: Serviço de vendas
        
    Raises:
        HTTPException: Se a venda não for encontrada
    """
    try:
        logger.info(f"Recebida solicitação para remover venda. ID: {sale_id}")
        
        deleted = await sale_service.delete_sale(sale_id)
        
        if not deleted:
            logger.warning(f"Venda não encontrada para remoção. ID: {sale_id}")
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        logger.info(f"Venda removida com sucesso. ID: {sale_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao remover venda {sale_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/statistics/summary")
async def get_sales_statistics(
    sale_service: SaleService = Depends(get_sale_service)
):
    """
    Obtém estatísticas das vendas.
    
    Args:
        sale_service: Serviço de vendas
        
    Returns:
        dict: Estatísticas das vendas
        
    Raises:
        HTTPException: Se houver erro ao obter estatísticas
    """
    try:
        logger.info("Recebida solicitação para obter estatísticas das vendas")
        
        # Usando o repositório diretamente para estatísticas
        sale_repository = SaleRepositoryImpl()
        statistics = await sale_repository.get_sales_statistics()
        
        logger.info("Estatísticas obtidas com sucesso")
        return statistics
        
    except Exception as e:
        logger.error(f"Erro inesperado ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
