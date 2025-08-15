from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, asc
from app.src.domain.ports.sale_repository import SaleRepositoryInterface
from app.src.domain.entities.sale_model import Sale
from app.src.infrastructure.driven.database.connection_mysql import get_session_factory
from datetime import date
import logging

logger = logging.getLogger(__name__)


class SaleRepositoryImpl(SaleRepositoryInterface):
    """
    Implementação do repositório de vendas usando SQLAlchemy.
    """

    def __init__(self):
        self.session_factory = get_session_factory()

    def _apply_value_ordering(self, query, order_by_value: Optional[str]):
        """
        Aplica ordenação por valor total da venda.
        
        Args:
            query: Query do SQLAlchemy
            order_by_value: 'asc' para crescente, 'desc' para decrescente
            
        Returns:
            Query com ordenação aplicada
        """
        if order_by_value == 'desc':
            return query.order_by(desc(Sale.total_amount))
        elif order_by_value == 'asc':
            return query.order_by(asc(Sale.total_amount))
        return query

    async def create_sale(self, sale: Sale) -> Sale:
        """
        Cria uma nova venda no banco de dados.
        
        Args:
            sale: Entidade da venda a ser criada
            
        Returns:
            Sale: Venda criada
        """
        try:
            logger.info(f"Criando venda no banco de dados")
            
            session = self.session_factory()
            try:
                session.add(sale)
                session.commit()
                session.refresh(sale)
                
                # Recarregar com relacionamentos
                created_sale = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.id == sale.id).first()
                
                session.expunge(created_sale)
                
                logger.info(f"Venda criada com sucesso. ID: {created_sale.id}")
                return created_sale
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao criar venda no banco de dados: {e}")
            raise e

    async def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        Busca uma venda pelo ID.
        
        Args:
            sale_id: ID da venda
            
        Returns:
            Optional[Sale]: Venda encontrada ou None
        """
        try:
            logger.info(f"Buscando venda por ID: {sale_id}")
            
            session = self.session_factory()
            try:
                sale = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.id == sale_id).first()
                
                if sale:
                    session.expunge(sale)
                    logger.info(f"Venda encontrada: {sale.id}")
                else:
                    logger.warning(f"Venda não encontrada: {sale_id}")
                
                return sale
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Erro ao buscar venda {sale_id}: {e}")
            raise e

    async def update_sale(self, sale_id: int, sale: Sale) -> Sale:
        """
        Atualiza uma venda existente.
        
        Args:
            sale_id: ID da venda
            sale: Dados atualizados da venda
            
        Returns:
            Sale: Venda atualizada
        """
        try:
            logger.info(f"Atualizando venda. ID: {sale_id}")
            
            session = self.session_factory()
            try:
                existing_sale = session.query(Sale).filter(Sale.id == sale_id).first()
                
                if not existing_sale:
                    raise ValueError(f"Venda não encontrada: {sale_id}")
                
                # Atualizar campos
                for field, value in sale.__dict__.items():
                    if not field.startswith('_') and value is not None:
                        setattr(existing_sale, field, value)
                
                session.commit()
                session.refresh(existing_sale)
                
                # Carregar relacionamentos
                updated_sale = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.id == sale_id).first()
                
                session.expunge(updated_sale)
                
                logger.info(f"Venda atualizada com sucesso. ID: {sale_id}")
                return updated_sale
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar venda {sale_id}: {e}")
            raise e

    async def update_sale_status(self, sale_id: int, status: str) -> Optional[Sale]:
        """
        Atualiza apenas o status de uma venda.
        
        Args:
            sale_id: ID da venda
            status: Novo status
            
        Returns:
            Optional[Sale]: Venda atualizada ou None se não encontrada
        """
        try:
            logger.info(f"Atualizando status da venda. ID: {sale_id}, Status: {status}")
            
            session = self.session_factory()
            try:
                existing_sale = session.query(Sale).filter(Sale.id == sale_id).first()
                
                if not existing_sale:
                    logger.warning(f"Venda não encontrada para atualização de status: {sale_id}")
                    return None
                
                existing_sale.status = status
                session.commit()
                session.refresh(existing_sale)
                
                # Carregar relacionamentos
                updated_sale = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.id == sale_id).first()
                
                session.expunge(updated_sale)
                
                logger.info(f"Status da venda atualizado com sucesso. ID: {sale_id}")
                return updated_sale
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da venda {sale_id}: {e}")
            raise e

    async def delete_sale(self, sale_id: int) -> bool:
        """
        Remove uma venda.
        
        Args:
            sale_id: ID da venda
            
        Returns:
            bool: True se removida com sucesso, False se não encontrada
        """
        try:
            logger.info(f"Removendo venda. ID: {sale_id}")
            
            session = self.session_factory()
            try:
                sale = session.query(Sale).filter(Sale.id == sale_id).first()
                
                if not sale:
                    logger.warning(f"Venda não encontrada para remoção: {sale_id}")
                    return False
                
                session.delete(sale)
                session.commit()
                
                logger.info(f"Venda removida com sucesso. ID: {sale_id}")
                return True
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao remover venda {sale_id}: {e}")
            raise e

    async def get_all_sales(self, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista todas as vendas com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas
        """
        try:
            logger.info(f"Listando todas as vendas. Skip: {skip}, Limit: {limit}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                )
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar todas as vendas: {e}")
            raise e

    async def get_sales_by_client(self, client_id: int, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista vendas por cliente.
        
        Args:
            client_id: ID do cliente
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas do cliente
        """
        try:
            logger.info(f"Listando vendas do cliente. ID: {client_id}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.client_id == client_id)
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas para o cliente {client_id}")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas do cliente {client_id}: {e}")
            raise e

    async def get_sales_by_employee(self, employee_id: int, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista vendas por funcionário.
        
        Args:
            employee_id: ID do funcionário
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas do funcionário
        """
        try:
            logger.info(f"Listando vendas do funcionário. ID: {employee_id}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.employee_id == employee_id)
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas para o funcionário {employee_id}")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas do funcionário {employee_id}: {e}")
            raise e

    async def get_sales_by_status(self, status: str, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista vendas por status.
        
        Args:
            status: Status das vendas
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas com o status especificado
        """
        try:
            logger.info(f"Listando vendas por status: {status}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.status == status)
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas com status {status}")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas por status {status}: {e}")
            raise e

    async def get_sales_by_payment_method(self, payment_method: str, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista vendas por forma de pagamento.
        
        Args:
            payment_method: Forma de pagamento
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas com a forma de pagamento especificada
        """
        try:
            logger.info(f"Listando vendas por forma de pagamento: {payment_method}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(Sale.payment_method == payment_method)
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas com forma de pagamento {payment_method}")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas por forma de pagamento {payment_method}: {e}")
            raise e

    async def get_sales_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Lista vendas em um período de datas.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas no período especificado
        """
        try:
            logger.info(f"Listando vendas por período: {start_date} a {end_date}, Order: {order_by_value}")
            
            session = self.session_factory()
            try:
                query = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(
                    and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
                )
                
                # Aplicar ordenação por valor se especificada
                query = self._apply_value_ordering(query, order_by_value)
                
                sales = query.offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas no período")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao listar vendas por período: {e}")
            raise e

    async def get_sales_statistics(self, start_date: Optional[date] = None, 
                                  end_date: Optional[date] = None) -> dict:
        """
        Obtém estatísticas das vendas.
        
        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            dict: Estatísticas das vendas
        """
        try:
            logger.info("Obtendo estatísticas das vendas")
            
            session = self.session_factory()
            try:
                # Query base
                base_query = session.query(Sale)
                
                # Aplicar filtro de data se fornecido
                if start_date and end_date:
                    base_query = base_query.filter(
                        and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
                    )
                
                # Total de vendas
                total_sales = base_query.count()
                
                # Vendas por status
                status_stats = {}
                for status in [Sale.STATUS_PENDENTE, Sale.STATUS_CONFIRMADA, Sale.STATUS_PAGA, Sale.STATUS_ENTREGUE, Sale.STATUS_CANCELADA]:
                    count = base_query.filter(Sale.status == status).count()
                    status_stats[status] = count
                
                # Vendas por forma de pagamento
                payment_stats = {}
                for payment in [Sale.PAYMENT_A_VISTA, Sale.PAYMENT_CARTAO_CREDITO, Sale.PAYMENT_CARTAO_DEBITO, Sale.PAYMENT_FINANCIAMENTO, Sale.PAYMENT_CONSORCIO, Sale.PAYMENT_PIX]:
                    count = base_query.filter(Sale.payment_method == payment).count()
                    payment_stats[payment] = count
                
                statistics = {
                    'total_sales': total_sales,
                    'sales_by_status': status_stats,
                    'sales_by_payment_method': payment_stats
                }
                
                if start_date and end_date:
                    statistics['period'] = {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                
                logger.info(f"Estatísticas obtidas. Total de vendas: {total_sales}")
                return statistics
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas das vendas: {e}")
            raise e

    async def search_sales(self, query: str, skip: int = 0, limit: int = 100) -> List[Sale]:
        """
        Busca vendas por termo geral.
        
        Args:
            query: Termo de busca
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        try:
            logger.info(f"Buscando vendas por termo: {query}")
            
            session = self.session_factory()
            try:
                # Buscar por ID, notas, status ou forma de pagamento
                sales = session.query(Sale).options(
                    selectinload(Sale.client),
                    selectinload(Sale.employee),
                    selectinload(Sale.vehicle)
                ).filter(
                    or_(
                        Sale.id.like(f"%{query}%"),
                        Sale.notes.like(f"%{query}%"),
                        Sale.status.like(f"%{query}%"),
                        Sale.payment_method.like(f"%{query}%")
                    )
                ).offset(skip).limit(limit).all()
                
                # Expunge all objects
                for sale in sales:
                    session.expunge(sale)
                
                logger.info(f"Encontradas {len(sales)} vendas para o termo '{query}'")
                return sales
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"Erro ao buscar vendas por termo '{query}': {e}")
            raise e
