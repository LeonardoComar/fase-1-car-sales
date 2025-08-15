from abc import ABC, abstractmethod
from typing import List, Optional
from app.src.domain.entities.vehicle_image_model import VehicleImage

class VehicleImageRepository(ABC):
    
    @abstractmethod
    def create(self, vehicle_image: VehicleImage) -> VehicleImage:
        """Criar uma nova imagem de veículo"""
        pass
    
    @abstractmethod
    def find_by_vehicle_id(self, vehicle_id: int) -> List[VehicleImage]:
        """Buscar todas as imagens de um veículo ordenadas por position"""
        pass
    
    @abstractmethod
    def find_by_id(self, image_id: int) -> Optional[VehicleImage]:
        """Buscar imagem por ID"""
        pass
    
    @abstractmethod
    def count_by_vehicle_id(self, vehicle_id: int) -> int:
        """Contar quantas imagens um veículo possui"""
        pass
    
    @abstractmethod
    def delete_by_id(self, image_id: int) -> bool:
        """Deletar uma imagem por ID"""
        pass
    
    @abstractmethod
    def delete_by_vehicle_id(self, vehicle_id: int) -> bool:
        """Deletar todas as imagens de um veículo"""
        pass
    
    @abstractmethod
    def update_positions(self, vehicle_id: int, positions: List[tuple]) -> bool:
        """Atualizar posições das imagens: [(image_id, new_position), ...]"""
        pass
    
    @abstractmethod
    def set_primary_image(self, vehicle_id: int, image_id: int) -> bool:
        """Definir uma imagem como principal"""
        pass
