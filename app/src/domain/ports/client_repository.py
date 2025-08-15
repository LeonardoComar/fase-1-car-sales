from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.client_model import Client, Address


class ClientRepositoryInterface(ABC):
    """
    Interface (porta) para o repositório de clientes.
    Define as operações que devem ser implementadas pela infraestrutura.
    """
    
    @abstractmethod
    async def create_client(self, address: Optional[Address], client: Client) -> Client:
        """
        Cria um novo cliente no banco de dados.
        
        Args:
            address: Dados do endereço (opcional)
            client: Dados do cliente
            
        Returns:
            Client: O cliente criado com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        pass
    
    @abstractmethod
    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """
        Busca um cliente pelo ID.
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        pass
    
    @abstractmethod
    async def update_client(self, client_id: int, address: Optional[Address], client: Client) -> Optional[Client]:
        """
        Atualiza um cliente existente.
        
        Args:
            client_id: ID do cliente
            address: Dados atualizados do endereço (opcional)
            client: Dados atualizados do cliente
            
        Returns:
            Optional[Client]: O cliente atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        pass
    
    @abstractmethod
    async def delete_client(self, client_id: int) -> bool:
        """
        Remove um cliente do banco de dados.
        
        Args:
            client_id: ID do cliente a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        pass
    
    @abstractmethod
    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Busca todos os clientes com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        pass
    
    @abstractmethod
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """
        Busca um cliente pelo email.
        
        Args:
            email: Email do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        pass
    
    @abstractmethod
    async def get_client_by_cpf(self, cpf: str) -> Optional[Client]:
        """
        Busca um cliente pelo CPF.
        
        Args:
            cpf: CPF do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        pass
    
    @abstractmethod
    async def search_clients_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Busca clientes por nome (busca parcial).
        
        Args:
            name: Nome ou parte do nome para buscar
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        pass
