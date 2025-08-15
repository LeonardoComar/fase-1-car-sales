from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.employee_model import Employee
from app.src.domain.entities.client_model import Address


class EmployeeRepositoryInterface(ABC):
    """
    Interface (porta) para o repositório de funcionários.
    Define as operações que devem ser implementadas pela infraestrutura.
    """
    
    @abstractmethod
    async def create_employee(self, address: Optional[Address], employee: Employee) -> Employee:
        """
        Cria um novo funcionário no banco de dados.
        
        Args:
            address: Dados do endereço (opcional)
            employee: Dados do funcionário
            
        Returns:
            Employee: O funcionário criado com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        pass
    
    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Busca um funcionário pelo ID.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        pass
    
    @abstractmethod
    async def update_employee(self, employee_id: int, address: Optional[Address], employee: Employee) -> Optional[Employee]:
        """
        Atualiza um funcionário existente.
        
        Args:
            employee_id: ID do funcionário
            address: Dados atualizados do endereço (opcional)
            employee: Dados atualizados do funcionário
            
        Returns:
            Optional[Employee]: O funcionário atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        pass
    
    @abstractmethod
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Remove um funcionário do banco de dados.
        
        Args:
            employee_id: ID do funcionário a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        pass
    
    @abstractmethod
    async def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca todos os funcionários com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        pass
    
    @abstractmethod
    async def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """
        Busca um funcionário pelo email.
        
        Args:
            email: Email do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        pass
    
    @abstractmethod
    async def get_employee_by_cpf(self, cpf: str) -> Optional[Employee]:
        """
        Busca um funcionário pelo CPF.
        
        Args:
            cpf: CPF do funcionário
            
        Returns:
            Optional[Employee]: O funcionário encontrado ou None
        """
        pass
    
    @abstractmethod
    async def search_employees_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca funcionários por nome (busca parcial).
        
        Args:
            name: Nome ou parte do nome para buscar
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        pass
    
    @abstractmethod
    async def get_employees_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Busca funcionários por status.
        
        Args:
            status: Status dos funcionários (Ativo/Inativo)
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Employee]: Lista de funcionários encontrados
        """
        pass
    
    @abstractmethod
    async def update_employee_status(self, employee_id: int, status: str) -> Optional[Employee]:
        """
        Atualiza apenas o status de um funcionário.
        
        Args:
            employee_id: ID do funcionário
            status: Novo status (Ativo/Inativo)
            
        Returns:
            Optional[Employee]: O funcionário atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        pass
