from abc import ABC, abstractmethod
from typing import Optional, List
from app.src.domain.entities.car_model import Car
from app.src.domain.entities.motor_vehicle_model import MotorVehicle


class CarRepositoryInterface(ABC):
    """
    Interface (porta) para o repositório de carros.
    Define as operações que devem ser implementadas pela infraestrutura.
    """
    
    @abstractmethod
    async def create_car(self, motor_vehicle: MotorVehicle, car: Car) -> Car:
        """
        Cria um novo carro no banco de dados.
        
        Args:
            motor_vehicle: Dados do veículo base
            car: Dados específicos do carro
            
        Returns:
            Car: O carro criado com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        pass
    
    @abstractmethod
    async def get_car_by_id(self, car_id: int) -> Optional[Car]:
        """
        Busca um carro pelo ID.
        
        Args:
            car_id: ID do carro
            
        Returns:
            Optional[Car]: O carro encontrado ou None
        """
        pass
    
    @abstractmethod
    async def update_car(self, car_id: int, motor_vehicle: MotorVehicle, car: Car) -> Optional[Car]:
        """
        Atualiza um carro existente.
        
        Args:
            car_id: ID do carro
            motor_vehicle: Dados atualizados do veículo base
            car: Dados atualizados do carro
            
        Returns:
            Optional[Car]: O carro atualizado ou None se não encontrado
        """
        pass
    
    @abstractmethod
    async def delete_car(self, car_id: int) -> bool:
        """
        Remove um carro do banco de dados.
        
        Args:
            car_id: ID do carro
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    async def get_active_cars_by_price(self) -> List[Car]:
        """
        Busca todos os carros com status 'Ativo' ordenados por preço (menor para maior).
        
        Returns:
            List[Car]: Lista de carros ativos ordenados por preço
        """
        pass
