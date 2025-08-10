from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.motorcycle_model import Motorcycle
from app.src.domain.entities.motor_vehicle_model import MotorVehicle


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
    async def get_active_motorcycles_by_price(self) -> List[Motorcycle]:
        """
        Busca todas as motos com status 'Ativo' ordenadas por preço (menor para maior).
        
        Returns:
            List[Motorcycle]: Lista de motos ativas ordenadas por preço
        """
        pass
