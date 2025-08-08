from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.src.domain.ports.car_repository import CarRepositoryInterface
from app.src.domain.entities.car_model import Car
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class CarRepository(CarRepositoryInterface):
    """
    Implementação concreta do repositório de carros.
    Adaptador que implementa a interface definida no domínio.
    """
    
    def __init__(self):
        pass
    
    async def create_car(self, motor_vehicle: MotorVehicle, car: Car) -> Car:
        """
        Cria um novo carro no banco de dados.
        Primeiro insere o motor_vehicle, depois o car com o ID gerado.
        """
        try:
            with get_db_session() as session:
                # Primeiro, insere o motor_vehicle
                session.add(motor_vehicle)
                session.flush()  # Para obter o ID gerado
                
                # Agora usa o ID gerado para criar o car
                car.vehicle_id = motor_vehicle.id
                session.add(car)
                
                session.commit()
                
                # Refresh para obter todos os dados atualizados
                session.refresh(motor_vehicle)
                session.refresh(car)
                
                # Eager load do relacionamento para evitar lazy loading após o fechamento da sessão
                car.motor_vehicle = motor_vehicle
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(motor_vehicle)
                session.expunge(car)
                
                logger.info(f"Carro criado com sucesso. ID: {motor_vehicle.id}")
                return car
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar carro: {str(e)}")
            raise Exception(f"Erro ao criar carro: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar carro: {str(e)}")
            raise Exception(f"Erro inesperado ao criar carro: {str(e)}")
    
    async def get_car_by_id(self, car_id: int) -> Optional[Car]:
        """
        Busca um carro pelo ID.
        """
        try:
            with get_db_session() as session:
                car = session.query(Car).filter(Car.vehicle_id == car_id).first()
                if car:
                    # Carregar o motor_vehicle relacionado
                    motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == car_id).first()
                    car.motor_vehicle = motor_vehicle
                    
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(motor_vehicle)
                    session.expunge(car)
                    
                return car
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar carro por ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao buscar carro: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar carro por ID {car_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar carro: {str(e)}")
    
    async def update_car(self, car_id: int, motor_vehicle: MotorVehicle, car: Car) -> Optional[Car]:
        """
        Atualiza um carro existente.
        """
        try:
            with get_db_session() as session:
                existing_car = session.query(Car).filter(Car.vehicle_id == car_id).first()
                existing_motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == car_id).first()
                
                if not existing_car or not existing_motor_vehicle:
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
                
                # Atualizar campos do carro
                existing_car.bodywork = car.bodywork
                existing_car.transmission = car.transmission
                
                session.commit()
                session.refresh(existing_car)
                session.refresh(existing_motor_vehicle)
                
                # Associar o motor_vehicle ao car
                existing_car.motor_vehicle = existing_motor_vehicle
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(existing_motor_vehicle)
                session.expunge(existing_car)
                
                logger.info(f"Carro atualizado com sucesso. ID: {car_id}")
                return existing_car
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao atualizar carro: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao atualizar carro: {str(e)}")
    
    async def delete_car(self, car_id: int) -> bool:
        """
        Remove um carro do banco de dados.
        Remove primeiro o carro, depois o motor_vehicle (CASCADE).
        """
        try:
            with get_db_session() as session:
                car = session.query(Car).filter(Car.vehicle_id == car_id).first()
                if not car:
                    return False
                
                motor_vehicle = session.query(MotorVehicle).filter(MotorVehicle.id == car_id).first()
                
                # Remove o carro primeiro
                session.delete(car)
                
                # Remove o motor_vehicle (o CASCADE já deveria remover o car, mas fazemos explicitamente)
                if motor_vehicle:
                    session.delete(motor_vehicle)
                
                session.commit()
                
                logger.info(f"Carro removido com sucesso. ID: {car_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao deletar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao deletar carro: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao deletar carro: {str(e)}")
