from typing import Optional
from app.src.domain.ports.car_repository import CarRepositoryInterface
from app.src.domain.entities.car_model import Car
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from app.src.application.dtos.car_dto import CreateCarRequest, CarResponse
import logging

logger = logging.getLogger(__name__)


class CarService:
    """
    Serviço de aplicação para operações relacionadas a carros.
    Coordena as operações entre a camada de apresentação e o domínio.
    """
    
    def __init__(self, car_repository: CarRepositoryInterface):
        self.car_repository = car_repository
    
    async def create_car(self, request: CreateCarRequest) -> CarResponse:
        """
        Cria um novo carro.
        
        Args:
            request: Dados para criação do carro
            
        Returns:
            CarResponse: Dados do carro criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Iniciando criação de carro: {request.model}")
            
            # Criar entidades do domínio
            motor_vehicle, car = Car.create_with_motor_vehicle(
                model=request.model,
                year=request.year,
                mileage=request.mileage,
                fuel_type=request.fuel_type,
                color=request.color,
                city=request.city,
                bodywork=request.bodywork,
                transmission=request.transmission,
                additional_description=request.additional_description
            )
            
            # Persistir no repositório
            created_car = await self.car_repository.create_car(motor_vehicle, car)
            
            # Converter para DTO de resposta
            response = self._car_to_response(created_car)
            
            logger.info(f"Carro criado com sucesso. ID: {response.id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao criar carro: {str(e)}")
            raise Exception(f"Erro ao criar carro: {str(e)}")
    
    async def get_car_by_id(self, car_id: int) -> Optional[CarResponse]:
        """
        Busca um carro pelo ID.
        
        Args:
            car_id: ID do carro
            
        Returns:
            Optional[CarResponse]: Dados do carro ou None se não encontrado
        """
        try:
            logger.info(f"Buscando carro por ID: {car_id}")
            
            car = await self.car_repository.get_car_by_id(car_id)
            if not car:
                logger.info(f"Carro não encontrado. ID: {car_id}")
                return None
            
            response = self._car_to_response(car)
            logger.info(f"Carro encontrado. ID: {car_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao buscar carro por ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao buscar carro: {str(e)}")
    
    async def update_car(self, car_id: int, request: CreateCarRequest) -> Optional[CarResponse]:
        """
        Atualiza um carro existente.
        
        Args:
            car_id: ID do carro
            request: Novos dados do carro
            
        Returns:
            Optional[CarResponse]: Dados do carro atualizado ou None se não encontrado
        """
        try:
            logger.info(f"Atualizando carro ID: {car_id}")
            
            # Criar entidades do domínio com todos os novos dados
            motor_vehicle = MotorVehicle(
                id=car_id,
                model=request.model,
                year=request.year,
                mileage=request.mileage,
                fuel_type=request.fuel_type,
                color=request.color,
                city=request.city,
                additional_description=request.additional_description
            )
            
            car = Car(
                vehicle_id=car_id,
                bodywork=request.bodywork,
                transmission=request.transmission
            )
            
            # Atualizar no repositório
            updated_car = await self.car_repository.update_car(car_id, motor_vehicle, car)
            if not updated_car:
                logger.info(f"Carro não encontrado para atualização. ID: {car_id}")
                return None
            
            response = self._car_to_response(updated_car)
            logger.info(f"Carro atualizado com sucesso. ID: {car_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao atualizar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao atualizar carro: {str(e)}")
    
    async def delete_car(self, car_id: int) -> bool:
        """
        Remove um carro.
        
        Args:
            car_id: ID do carro
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
        """
        try:
            logger.info(f"Removendo carro ID: {car_id}")
            
            result = await self.car_repository.delete_car(car_id)
            if result:
                logger.info(f"Carro removido com sucesso. ID: {car_id}")
            else:
                logger.info(f"Carro não encontrado para remoção. ID: {car_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao remover carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao remover carro: {str(e)}")
    
    async def inactivate_car(self, car_id: int) -> Optional[CarResponse]:
        """
        Inativa um carro alterando seu status para 'Inativo'.
        
        Args:
            car_id: ID do carro
            
        Returns:
            Optional[CarResponse]: Dados do carro inativado ou None se não encontrado
        """
        try:
            logger.info(f"Inativando carro ID: {car_id}")
            
            # Buscar o carro atual
            current_car = await self.car_repository.get_car_by_id(car_id)
            if not current_car:
                logger.info(f"Carro não encontrado para inativação. ID: {car_id}")
                return None
            
            # Criar entidade motor_vehicle com status 'Inativo', mantendo os outros dados
            motor_vehicle = current_car.motor_vehicle
            motor_vehicle.status = 'Inativo'
            
            # Atualizar no repositório
            updated_car = await self.car_repository.update_car(car_id, motor_vehicle, current_car)
            if not updated_car:
                logger.info(f"Falha ao inativar carro. ID: {car_id}")
                return None
            
            response = self._car_to_response(updated_car)
            logger.info(f"Carro inativado com sucesso. ID: {car_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao inativar carro ID {car_id}: {str(e)}")
            raise Exception(f"Erro ao inativar carro: {str(e)}")
    
    def _car_to_response(self, car: Car) -> CarResponse:
        """
        Converte uma entidade Car para CarResponse.
        
        Args:
            car: Entidade do domínio
            
        Returns:
            CarResponse: DTO de resposta
        """
        motor_vehicle = car.motor_vehicle
        
        return CarResponse(
            id=motor_vehicle.id,
            model=motor_vehicle.model,
            year=motor_vehicle.year,
            mileage=motor_vehicle.mileage,
            fuel_type=motor_vehicle.fuel_type,
            color=motor_vehicle.color,
            city=motor_vehicle.city,
            additional_description=motor_vehicle.additional_description,
            status=motor_vehicle.status,
            bodywork=car.bodywork,
            transmission=car.transmission,
            created_at=motor_vehicle.created_at.isoformat() if motor_vehicle.created_at else "",
            updated_at=motor_vehicle.updated_at.isoformat() if motor_vehicle.updated_at else ""
        )
