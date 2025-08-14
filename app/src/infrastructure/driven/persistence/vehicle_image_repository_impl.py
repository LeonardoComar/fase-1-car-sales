from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.src.domain.entities.vehicle_image_model import VehicleImage
from app.src.domain.ports.vehicle_image_repository import VehicleImageRepository
from app.src.infrastructure.driven.database.connection_mysql import get_session_factory

class VehicleImageRepositoryImpl(VehicleImageRepository):
    
    def __init__(self):
        self.session_factory = get_session_factory()
    
    def create(self, vehicle_image: VehicleImage) -> VehicleImage:
        """Criar uma nova imagem de veículo"""
        session: Session = self.session_factory()
        try:
            session.add(vehicle_image)
            session.commit()
            session.refresh(vehicle_image)
            return vehicle_image
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def find_by_vehicle_id(self, vehicle_id: int) -> List[VehicleImage]:
        """Buscar todas as imagens de um veículo ordenadas por position"""
        session: Session = self.session_factory()
        try:
            images = session.query(VehicleImage)\
                .filter(VehicleImage.vehicle_id == vehicle_id)\
                .order_by(VehicleImage.position.asc())\
                .all()
            
            # Expunge para evitar problemas de sessão
            for image in images:
                session.expunge(image)
            
            return images
        finally:
            session.close()
    
    def find_by_id(self, image_id: int) -> Optional[VehicleImage]:
        """Buscar imagem por ID"""
        session: Session = self.session_factory()
        try:
            image = session.query(VehicleImage).filter(VehicleImage.id == image_id).first()
            if image:
                session.expunge(image)
            return image
        finally:
            session.close()
    
    def count_by_vehicle_id(self, vehicle_id: int) -> int:
        """Contar quantas imagens um veículo possui"""
        session: Session = self.session_factory()
        try:
            return session.query(VehicleImage)\
                .filter(VehicleImage.vehicle_id == vehicle_id)\
                .count()
        finally:
            session.close()
    
    def delete_by_id(self, image_id: int) -> bool:
        """Deletar uma imagem por ID"""
        session: Session = self.session_factory()
        try:
            image = session.query(VehicleImage).filter(VehicleImage.id == image_id).first()
            if image:
                session.delete(image)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_by_vehicle_id(self, vehicle_id: int) -> bool:
        """Deletar todas as imagens de um veículo"""
        session: Session = self.session_factory()
        try:
            deleted_count = session.query(VehicleImage)\
                .filter(VehicleImage.vehicle_id == vehicle_id)\
                .delete()
            session.commit()
            return deleted_count > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_positions(self, vehicle_id: int, positions: List[tuple]) -> bool:
        """Atualizar posições das imagens: [(image_id, new_position), ...]"""
        session: Session = self.session_factory()
        try:
            for image_id, new_position in positions:
                session.query(VehicleImage)\
                    .filter(VehicleImage.id == image_id, VehicleImage.vehicle_id == vehicle_id)\
                    .update({VehicleImage.position: new_position})
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def set_primary_image(self, vehicle_id: int, image_id: int) -> bool:
        """Definir uma imagem como principal"""
        session: Session = self.session_factory()
        try:
            # Primeiro, remover primary de todas as imagens do veículo
            session.query(VehicleImage)\
                .filter(VehicleImage.vehicle_id == vehicle_id)\
                .update({VehicleImage.is_primary: False})
            
            # Depois, definir a imagem específica como primary
            updated = session.query(VehicleImage)\
                .filter(VehicleImage.id == image_id, VehicleImage.vehicle_id == vehicle_id)\
                .update({VehicleImage.is_primary: True})
            
            session.commit()
            return updated > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
