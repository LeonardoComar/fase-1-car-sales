from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from app.src.domain.ports.motorcycle_repository import MotorcycleRepositoryInterface
from app.src.domain.entities.motorcycle_model import Motorcycle
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class MotorcycleRepository(MotorcycleRepositoryInterface):
    """
    Implementação concreta do repositório de motos.
    Adaptador que implementa a interface definida no domínio.
    """
    
    def __init__(self):
        pass
    
    async def create_motorcycle(self, motor_vehicle: MotorVehicle, motorcycle: Motorcycle) -> Motorcycle:
        """
        Cria uma nova moto no banco de dados.
        Primeiro insere o motor_vehicle, depois a motorcycle com o ID gerado.
        """
        try:
            with get_db_session() as session:
                # Primeiro, insere o motor_vehicle
                session.add(motor_vehicle)
                session.flush()  # Para obter o ID gerado
                
                # Agora usa o ID gerado para criar a motorcycle
                motorcycle.vehicle_id = motor_vehicle.id
                session.add(motorcycle)
                
                session.commit()
                
                # Refresh para obter todos os dados atualizados
                session.refresh(motor_vehicle)
                session.refresh(motorcycle)
                
                # Eager load do relacionamento para evitar lazy loading após o fechamento da sessão
                motorcycle.motor_vehicle = motor_vehicle
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(motor_vehicle)
                session.expunge(motorcycle)
                
                logger.info(f"Moto criada com sucesso. ID: {motor_vehicle.id}")
                return motorcycle
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar moto: {str(e)}")
            raise Exception(f"Erro ao criar moto: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar moto: {str(e)}")
            raise Exception(f"Erro inesperado ao criar moto: {str(e)}")
    
    async def get_motorcycle_by_id(self, motorcycle_id: int) -> Optional[Motorcycle]:
        """
        Busca uma moto pelo ID.
        """
        try:
            with get_db_session() as session:
                motorcycle = session.query(Motorcycle).filter(Motorcycle.vehicle_id == motorcycle_id).first()
                if motorcycle:
                    # Carregar o motor_vehicle relacionado
                    motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == motorcycle_id).first()
                    motorcycle.motor_vehicle = motor_vehicle
                    
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(motor_vehicle)
                    session.expunge(motorcycle)
                    
                return motorcycle
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar moto por ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao buscar moto: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar moto por ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar moto: {str(e)}")
    
    async def update_motorcycle(self, motorcycle_id: int, motor_vehicle: MotorVehicle, motorcycle: Motorcycle) -> Optional[Motorcycle]:
        """
        Atualiza uma moto existente.
        """
        try:
            with get_db_session() as session:
                existing_motorcycle = session.query(Motorcycle).filter(Motorcycle.vehicle_id == motorcycle_id).first()
                existing_motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == motorcycle_id).first()
                
                if not existing_motorcycle or not existing_motor_vehicle:
                    return None
                
                # Atualizar campos do motor_vehicle
                existing_motor_vehicle.model = motor_vehicle.model
                existing_motor_vehicle.year = motor_vehicle.year
                existing_motor_vehicle.mileage = motor_vehicle.mileage
                existing_motor_vehicle.fuel_type = motor_vehicle.fuel_type
                existing_motor_vehicle.color = motor_vehicle.color
                existing_motor_vehicle.city = motor_vehicle.city
                existing_motor_vehicle.price = motor_vehicle.price
                existing_motor_vehicle.additional_description = motor_vehicle.additional_description
                existing_motor_vehicle.status = motor_vehicle.status
                
                # Atualizar campos da moto
                existing_motorcycle.starter = motorcycle.starter
                existing_motorcycle.fuel_system = motorcycle.fuel_system
                existing_motorcycle.engine_displacement = motorcycle.engine_displacement
                existing_motorcycle.cooling = motorcycle.cooling
                existing_motorcycle.style = motorcycle.style
                existing_motorcycle.engine_type = motorcycle.engine_type
                existing_motorcycle.gears = motorcycle.gears
                existing_motorcycle.front_rear_brake = motorcycle.front_rear_brake
                
                session.commit()
                session.refresh(existing_motorcycle)
                session.refresh(existing_motor_vehicle)
                
                # Associar o motor_vehicle à motorcycle
                existing_motorcycle.motor_vehicle = existing_motor_vehicle
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(existing_motor_vehicle)
                session.expunge(existing_motorcycle)
                
                logger.info(f"Moto atualizada com sucesso. ID: {motorcycle_id}")
                return existing_motorcycle
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao atualizar moto: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao atualizar moto: {str(e)}")
    
    async def delete_motorcycle(self, motorcycle_id: int) -> bool:
        """
        Remove uma moto do banco de dados.
        Remove primeiro a motorcycle, depois o motor_vehicle (CASCADE).
        """
        try:
            with get_db_session() as session:
                motorcycle = session.query(Motorcycle).filter(Motorcycle.vehicle_id == motorcycle_id).first()
                if not motorcycle:
                    return False
                
                motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == motorcycle_id).first()
                
                # Remove a motorcycle primeiro
                session.delete(motorcycle)
                
                # Remove o motor_vehicle (o CASCADE já deveria remover a motorcycle, mas fazemos explicitamente)
                if motor_vehicle:
                    session.delete(motor_vehicle)
                
                session.commit()
                
                logger.info(f"Moto removida com sucesso. ID: {motorcycle_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao deletar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao deletar moto: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao deletar moto: {str(e)}")

    async def get_active_motorcycles_by_price(self) -> List[Motorcycle]:
        """
        Busca todas as motos com status 'Ativo' ordenadas por preço (menor para maior).
        """
        try:
            with get_db_session() as session:
                # Query que junta as tabelas motor_vehicle e motorcycle
                # Filtra por status 'Ativo' e ordena por preço
                query = session.query(Motorcycle).join(MotorVehicle).filter(
                    MotorVehicle.status == 'Ativo'
                ).order_by(MotorVehicle.price.asc())
                
                motorcycles = query.all()
                
                # Carregar eager load dos relacionamentos para evitar lazy loading
                for motorcycle in motorcycles:
                    # Forçar o carregamento do motor_vehicle
                    _ = motorcycle.motor_vehicle.model
                    
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(motorcycle.motor_vehicle)
                    session.expunge(motorcycle)
                
                logger.info(f"Encontradas {len(motorcycles)} motos ativas ordenadas por preço")
                return motorcycles
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar motos ativas por preço: {str(e)}")
            raise Exception(f"Erro ao buscar motos ativas: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar motos ativas por preço: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar motos ativas: {str(e)}")
