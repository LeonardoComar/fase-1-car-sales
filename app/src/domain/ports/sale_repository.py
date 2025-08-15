from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.sale_model import Sale
from datetime import date


class SaleRepositoryInterface(ABC):
    """
    Interface para o repositório de vendas.
    """

    @abstractmethod
    async def create_sale(self, sale: Sale) -> Sale:
        """
        Cria uma nova venda no repositório.
        
        Args:
            sale: Entidade da venda
            
        Returns:
            Sale: A venda criada com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        pass

    @abstractmethod
    async def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        Busca uma venda pelo ID.
        
        Args:
            sale_id: ID da venda
            
        Returns:
            Optional[Sale]: A venda encontrada ou None
        """
        pass

    @abstractmethod
    async def update_sale(self, sale_id: int, sale: Sale) -> Optional[Sale]:
        """
        Atualiza uma venda existente.
        
        Args:
            sale_id: ID da venda
            sale: Dados atualizados da venda
            
        Returns:
            Optional[Sale]: A venda atualizada ou None se não encontrada
            
        Raises:
            Exception: Se houver erro na atualização
        """
        pass

    @abstractmethod
    async def update_sale_status(self, sale_id: int, status: str) -> Optional[Sale]:
        """
        Atualiza apenas o status de uma venda.
        
        Args:
            sale_id: ID da venda
            status: Novo status
            
        Returns:
            Optional[Sale]: A venda atualizada ou None se não encontrada
            
        Raises:
            Exception: Se houver erro na atualização
        """
        pass

    @abstractmethod
    async def delete_sale(self, sale_id: int) -> bool:
        """
        Remove uma venda do repositório.
        
        Args:
            sale_id: ID da venda a ser removida
            
        Returns:
            bool: True se removida com sucesso, False se não encontrada
            
        Raises:
            Exception: Se houver erro na remoção
        """
        pass

    @abstractmethod
    async def get_all_sales(self, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca todas as vendas com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_by_client(self, client_id: int, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca vendas por cliente.
        
        Args:
            client_id: ID do cliente
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_by_employee(self, employee_id: int, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca vendas por funcionário.
        
        Args:
            employee_id: ID do funcionário
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_by_status(self, status: str, skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca vendas por status.
        
        Args:
            status: Status das vendas
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_by_date_range(self, start_date: date, end_date: date, 
                                     skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca vendas por período.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_by_payment_method(self, payment_method: str, 
                                         skip: int = 0, limit: int = 100, order_by_value: Optional[str] = None) -> List[Sale]:
        """
        Busca vendas por forma de pagamento.
        
        Args:
            payment_method: Forma de pagamento
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_value: Ordenação por valor - 'asc' ou 'desc' (opcional)
            
        Returns:
            List[Sale]: Lista de vendas encontradas
        """
        pass

    @abstractmethod
    async def get_sales_statistics(self, start_date: Optional[date] = None, 
                                  end_date: Optional[date] = None) -> dict:
        """
        Busca estatísticas de vendas.
        
        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            dict: Estatísticas das vendas
        """
        pass
