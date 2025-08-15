from typing import Optional, List
from app.src.domain.ports.sale_repository import SaleRepositoryInterface
from app.src.domain.ports.car_repository import CarRepositoryInterface
from app.src.domain.ports.motorcycle_repository import MotorcycleRepositoryInterface
from app.src.domain.entities.sale_model import Sale
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from app.src.application.dtos.sale_dto import (
    CreateSaleRequest, UpdateSaleRequest, SaleResponse, 
    SaleListResponse, SalesListResponse, ClientSummary,
    EmployeeSummary, VehicleSummary
)
from decimal import Decimal
from datetime import date
import logging

logger = logging.getLogger(__name__)


class SaleService:
    """
    Serviço de aplicação para vendas.
    """

    def __init__(self, sale_repository: SaleRepositoryInterface, 
                 car_repository: CarRepositoryInterface,
                 motorcycle_repository: MotorcycleRepositoryInterface):
        self.sale_repository = sale_repository
        self.car_repository = car_repository
        self.motorcycle_repository = motorcycle_repository

    async def create_sale(self, request: CreateSaleRequest) -> SaleResponse:
        """
        Cria uma nova venda.
        
        Args:
            request: Dados da venda a ser criada
            
        Returns:
            SaleResponse: Dados da venda criada
        """
        try:
            logger.info(f"Iniciando criação de venda. Cliente: {request.client_id}, Veículo: {request.vehicle_id}")
            
            # Validar forma de pagamento
            if not Sale.is_valid_payment_method(request.payment_method):
                raise ValueError(f"Forma de pagamento inválida: {request.payment_method}")
            
            # Validar se desconto não é maior que valor total
            if request.discount_amount and request.discount_amount > request.total_amount:
                raise ValueError("Desconto não pode ser maior que o valor total")
            
            # Criar entidade Sale
            sale = Sale.create_sale(
                client_id=request.client_id,
                employee_id=request.employee_id,
                vehicle_id=request.vehicle_id,
                total_amount=request.total_amount,
                payment_method=request.payment_method,
                sale_date=request.sale_date,
                notes=request.notes,
                discount_amount=request.discount_amount or Decimal('0.00'),
                tax_amount=request.tax_amount or Decimal('0.00'),
                commission_rate=request.commission_rate or Decimal('0.00')
            )
            
            created_sale = await self.sale_repository.create_sale(sale)
            
            logger.info(f"Venda criada com sucesso. ID: {created_sale.id}")
            return self._convert_to_sale_response(created_sale)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao criar venda: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao criar venda: {e}")
            raise Exception(f"Erro interno do servidor ao criar venda: {str(e)}")

    async def get_sale_by_id(self, sale_id: int) -> Optional[SaleResponse]:
        """
        Busca uma venda pelo ID.
        
        Args:
            sale_id: ID da venda
            
        Returns:
            Optional[SaleResponse]: Dados da venda ou None se não encontrada
        """
        try:
            logger.info(f"Buscando venda por ID: {sale_id}")
            
            sale = await self.sale_repository.get_sale_by_id(sale_id)
            
            if not sale:
                logger.warning(f"Venda não encontrada. ID: {sale_id}")
                return None
            
            logger.info(f"Venda encontrada: {sale.id}")
            return self._convert_to_sale_response(sale)
            
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar venda {sale_id}: {e}")
            raise Exception(f"Erro interno do servidor ao buscar venda: {str(e)}")

    async def update_sale(self, sale_id: int, request: UpdateSaleRequest) -> Optional[SaleResponse]:
        """
        Atualiza uma venda existente.
        
        Args:
            sale_id: ID da venda
            request: Dados para atualização
            
        Returns:
            Optional[SaleResponse]: Dados da venda atualizada ou None se não encontrada
        """
        try:
            logger.info(f"Iniciando atualização de venda. ID: {sale_id}")
            
            # Buscar venda existente
            existing_sale = await self.sale_repository.get_sale_by_id(sale_id)
            if not existing_sale:
                logger.warning(f"Venda não encontrada para atualização. ID: {sale_id}")
                return None
            
            # Validar forma de pagamento se fornecida
            if request.payment_method and not Sale.is_valid_payment_method(request.payment_method):
                raise ValueError(f"Forma de pagamento inválida: {request.payment_method}")
            
            # Validar status se fornecido
            if request.status and not Sale.is_valid_status(request.status):
                raise ValueError(f"Status inválido: {request.status}")
            
            # Validar desconto
            total_amount = request.total_amount or existing_sale.total_amount
            discount_amount = request.discount_amount or existing_sale.discount_amount
            if discount_amount > total_amount:
                raise ValueError("Desconto não pode ser maior que o valor total")
            
            # Atualizar campos
            existing_sale.update_fields(
                total_amount=request.total_amount,
                payment_method=request.payment_method,
                status=request.status,
                sale_date=request.sale_date,
                notes=request.notes,
                discount_amount=request.discount_amount,
                tax_amount=request.tax_amount,
                commission_rate=request.commission_rate
            )
            
            updated_sale = await self.sale_repository.update_sale(sale_id, existing_sale)
            
            logger.info(f"Venda atualizada com sucesso. ID: {sale_id}")
            return self._convert_to_sale_response(updated_sale)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar venda {sale_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar venda {sale_id}: {e}")
            raise Exception(f"Erro interno do servidor ao atualizar venda: {str(e)}")

    async def update_sale_status(self, sale_id: int, status: str) -> Optional[SaleResponse]:
        """
        Atualiza apenas o status de uma venda.
        Se o status for "Confirmada", também atualiza o status do veículo para "Vendido".
        
        Args:
            sale_id: ID da venda
            status: Novo status
            
        Returns:
            Optional[SaleResponse]: Dados da venda atualizada ou None se não encontrada
        """
        try:
            logger.info(f"Iniciando atualização de status da venda. ID: {sale_id}, Status: {status}")
            
            # Validar status
            if not Sale.is_valid_status(status):
                raise ValueError(f"Status inválido: {status}")
            
            # Buscar a venda para obter o vehicle_id antes da atualização
            existing_sale = await self.sale_repository.get_sale_by_id(sale_id)
            if not existing_sale:
                logger.warning(f"Venda não encontrada para atualização de status. ID: {sale_id}")
                return None
            
            # Atualizar status da venda
            updated_sale = await self.sale_repository.update_sale_status(sale_id, status)
            
            if not updated_sale:
                logger.warning(f"Venda não encontrada para atualização de status. ID: {sale_id}")
                return None
            
            # Se o status for "Confirmada", atualizar o status do veículo para "Vendido"
            if status == Sale.STATUS_CONFIRMADA:
                vehicle_id = existing_sale.vehicle_id
                logger.info(f"Atualizando status do veículo para 'Vendido'. Vehicle ID: {vehicle_id}")
                
                # Tentar atualizar como carro primeiro, depois como moto
                car_updated = await self.car_repository.update_vehicle_status(vehicle_id, MotorVehicle.STATUS_VENDIDO)
                
                if not car_updated:
                    # Se não foi um carro, tentar como moto
                    motorcycle_updated = await self.motorcycle_repository.update_vehicle_status(vehicle_id, MotorVehicle.STATUS_VENDIDO)
                    
                    if not motorcycle_updated:
                        logger.warning(f"Não foi possível atualizar o status do veículo ID: {vehicle_id}")
                    else:
                        logger.info(f"Status da motocicleta atualizado para 'Vendido'. Vehicle ID: {vehicle_id}")
                else:
                    logger.info(f"Status do carro atualizado para 'Vendido'. Vehicle ID: {vehicle_id}")

            logger.info(f"Status da venda atualizado com sucesso. ID: {sale_id}")
            return self._convert_to_sale_response(updated_sale)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar status da venda {sale_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar status da venda {sale_id}: {e}")
            raise Exception(f"Erro interno do servidor ao atualizar status: {str(e)}")

    async def delete_sale(self, sale_id: int) -> bool:
        """
        Remove uma venda.
        
        Args:
            sale_id: ID da venda
            
        Returns:
            bool: True se removida com sucesso, False se não encontrada
        """
        try:
            logger.info(f"Iniciando remoção de venda. ID: {sale_id}")
            
            deleted = await self.sale_repository.delete_sale(sale_id)
            
            if deleted:
                logger.info(f"Venda removida com sucesso. ID: {sale_id}")
            else:
                logger.warning(f"Venda não encontrada para remoção. ID: {sale_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Erro inesperado ao remover venda {sale_id}: {e}")
            raise Exception(f"Erro interno do servidor ao remover venda: {str(e)}")

    async def get_sales_with_filters(self, skip: int = 0, limit: int = 100,
                                   client_id: Optional[int] = None, employee_id: Optional[int] = None,
                                   status: Optional[str] = None, payment_method: Optional[str] = None,
                                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                                   order_by_value: Optional[str] = None) -> List[SaleListResponse]:
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
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[SaleListResponse]: Lista de vendas
        """
        try:
            logger.info(f"Listando vendas com filtros. Skip: {skip}, Limit: {limit}")
            
            # Aplicar filtros em ordem de prioridade
            if start_date and end_date:
                sales = await self.sale_repository.get_sales_by_date_range(start_date, end_date, skip, limit, order_by_value)
            elif client_id:
                sales = await self.sale_repository.get_sales_by_client(client_id, skip, limit, order_by_value)
            elif employee_id:
                sales = await self.sale_repository.get_sales_by_employee(employee_id, skip, limit, order_by_value)
            elif status:
                sales = await self.sale_repository.get_sales_by_status(status, skip, limit, order_by_value)
            elif payment_method:
                sales = await self.sale_repository.get_sales_by_payment_method(payment_method, skip, limit, order_by_value)
            else:
                sales = await self.sale_repository.get_all_sales(skip, limit, order_by_value)
            
            logger.info(f"Encontradas {len(sales)} vendas")
            return [self._convert_to_sale_list_response(sale) for sale in sales]
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas com filtros: {e}")
            raise Exception(f"Erro interno do servidor ao listar vendas: {str(e)}")

    def _convert_to_sale_response(self, sale: Sale) -> SaleResponse:
        """
        Converte uma entidade Sale para SaleResponse.
        
        Args:
            sale: Entidade da venda
            
        Returns:
            SaleResponse: DTO de resposta da venda
        """
        # Criar resumos das entidades relacionadas
        client_summary = ClientSummary(
            id=sale.client.id,
            name=sale.client.name,
            email=sale.client.email,
            cpf=sale.client.cpf
        )
        
        employee_summary = EmployeeSummary(
            id=sale.employee.id,
            name=sale.employee.name,
            email=sale.employee.email
        )
        
        vehicle_summary = VehicleSummary(
            id=sale.vehicle.id,
            model=sale.vehicle.model,
            year=sale.vehicle.year,
            color=sale.vehicle.color,
            price=sale.vehicle.price
        )
        
        return SaleResponse(
            id=sale.id,
            client=client_summary,
            employee=employee_summary,
            vehicle=vehicle_summary,
            total_amount=sale.total_amount,
            payment_method=sale.payment_method,
            status=sale.status,
            sale_date=sale.sale_date.isoformat(),
            notes=sale.notes,
            discount_amount=sale.discount_amount,
            tax_amount=sale.tax_amount,
            commission_rate=sale.commission_rate,
            commission_amount=sale.commission_amount,
            final_amount=sale.calculate_final_amount(),
            created_at=sale.created_at.isoformat() if sale.created_at else "",
            updated_at=sale.updated_at.isoformat() if sale.updated_at else ""
        )

    def _convert_to_sale_list_response(self, sale: Sale) -> SaleListResponse:
        """
        Converte uma entidade Sale para SaleListResponse.
        
        Args:
            sale: Entidade da venda
            
        Returns:
            SaleListResponse: DTO de resposta simplificada da venda
        """
        return SaleListResponse(
            id=sale.id,
            client_name=sale.client.name if sale.client else "N/A",
            employee_name=sale.employee.name if sale.employee else "N/A",
            vehicle_model=f"{sale.vehicle.model} {sale.vehicle.year}" if sale.vehicle else "N/A",
            total_amount=sale.total_amount,
            payment_method=sale.payment_method,
            status=sale.status,
            sale_date=sale.sale_date.isoformat(),
            final_amount=sale.calculate_final_amount()
        )
