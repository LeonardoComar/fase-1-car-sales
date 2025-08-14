from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.motorcycle_model import Motorcycle
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from decimal import Decimal


class MotorcycleRepositoryInterface(ABC):
    """
    Interface (porta) para o repositório de motos.
    Define as operações que devem ser implementadas pela infraestrutura.
    """
    
    @abstractmethod
    async def create_motorcycle(self, motor_vehicle: MotorVehicle, motorcycle: Motorcycle) -> Motorcycle:
        """
        Cria uma nova moto no banco de dados.
        
        Args:
            motor_vehicle: Dados do veículo base
            motorcycle: Dados específicos da moto
            
        Returns:
            Motorcycle: A moto criada com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        pass
    
    @abstractmethod
    async def get_motorcycle_by_id(self, motorcycle_id: int) -> Optional[Motorcycle]:
        """
        Busca uma moto pelo ID.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            Optional[Motorcycle]: A moto encontrada ou None
        """
        pass
    
    @abstractmethod
    async def update_motorcycle(self, motorcycle_id: int, motor_vehicle: MotorVehicle, motorcycle: Motorcycle) -> Optional[Motorcycle]:
        """
        Atualiza uma moto existente.
        
        Args:
            motorcycle_id: ID da moto
            motor_vehicle: Dados atualizados do veículo base
            motorcycle: Dados atualizados da moto
            
        Returns:
            Optional[Motorcycle]: A moto atualizada ou None se não encontrada
        """
        pass
    
    @abstractmethod
    async def delete_motorcycle(self, motorcycle_id: int) -> bool:
        """
        Remove uma moto do banco de dados.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            bool: True se removida com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    async def get_all_motorcycles(self, skip: int = 0, limit: int = 100, order_by_price: Optional[str] = None, 
                                 status: Optional[str] = None, min_price: Optional[Decimal] = None, 
                                 max_price: Optional[Decimal] = None) -> List[Motorcycle]:
        """
        Busca todas as motocicletas com filtros opcionais.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            order_by_price: Ordenação por preço - 'asc' ou 'desc' (opcional)
            status: Status das motocicletas para filtrar (opcional)
            min_price: Preço mínimo para filtrar (opcional)
            max_price: Preço máximo para filtrar (opcional)
            
        Returns:
            List[Motorcycle]: Lista de motocicletas encontradas
        """
        pass
