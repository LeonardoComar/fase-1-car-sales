from typing import Optional, List
from app.src.domain.ports.motorcycle_repository import MotorcycleRepositoryInterface
from app.src.domain.entities.motorcycle_model import Motorcycle
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from app.src.application.dtos.motorcycle_dto import CreateMotorcycleRequest, MotorcycleResponse
import logging

logger = logging.getLogger(__name__)


class MotorcycleService:
    """
    Serviço de aplicação para operações relacionadas a motos.
    Coordena as operações entre a camada de apresentação e o domínio.
    """
    
    def __init__(self, motorcycle_repository: MotorcycleRepositoryInterface):
        self.motorcycle_repository = motorcycle_repository
    
    async def create_motorcycle(self, request: CreateMotorcycleRequest) -> MotorcycleResponse:
        """
        Cria uma nova moto.
        
        Args:
            request: Dados para criação da moto
            
        Returns:
            MotorcycleResponse: Dados da moto criada
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Iniciando criação de moto: {request.model}")
            
            # Criar entidades do domínio
            motor_vehicle, motorcycle = Motorcycle.create_with_motor_vehicle(
                model=request.model,
                year=request.year,
                mileage=request.mileage,
                fuel_type=request.fuel_type,
                color=request.color,
                city=request.city,
                price=request.price,
                starter=request.starter,
                fuel_system=request.fuel_system,
                engine_displacement=request.engine_displacement,
                cooling=request.cooling,
                style=request.style,
                engine_type=request.engine_type,
                gears=request.gears,
                front_rear_brake=request.front_rear_brake,
                additional_description=request.additional_description
            )
            
            # Persistir no repositório
            created_motorcycle = await self.motorcycle_repository.create_motorcycle(motor_vehicle, motorcycle)
            
            # Converter para DTO de resposta
            response = self._motorcycle_to_response(created_motorcycle)
            
            logger.info(f"Moto criada com sucesso. ID: {response.id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao criar moto: {str(e)}")
            raise Exception(f"Erro ao criar moto: {str(e)}")
    
    async def get_motorcycle_by_id(self, motorcycle_id: int) -> Optional[MotorcycleResponse]:
        """
        Busca uma moto pelo ID.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            Optional[MotorcycleResponse]: Dados da moto ou None se não encontrada
        """
        try:
            logger.info(f"Buscando moto por ID: {motorcycle_id}")
            
            motorcycle = await self.motorcycle_repository.get_motorcycle_by_id(motorcycle_id)
            if not motorcycle:
                logger.info(f"Moto não encontrada. ID: {motorcycle_id}")
                return None
            
            response = self._motorcycle_to_response(motorcycle)
            logger.info(f"Moto encontrada. ID: {motorcycle_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao buscar moto por ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao buscar moto: {str(e)}")
    
    async def update_motorcycle(self, motorcycle_id: int, request: CreateMotorcycleRequest) -> Optional[MotorcycleResponse]:
        """
        Atualiza uma moto existente.
        
        Args:
            motorcycle_id: ID da moto
            request: Novos dados da moto
            
        Returns:
            Optional[MotorcycleResponse]: Dados da moto atualizada ou None se não encontrada
        """
        try:
            logger.info(f"Atualizando moto ID: {motorcycle_id}")
            
            # Criar entidades do domínio com todos os novos dados
            motor_vehicle = MotorVehicle(
                id=motorcycle_id,
                model=request.model,
                year=request.year,
                mileage=request.mileage,
                fuel_type=request.fuel_type,
                color=request.color,
                city=request.city,
                price=request.price,
                additional_description=request.additional_description
            )
            
            motorcycle = Motorcycle(
                vehicle_id=motorcycle_id,
                starter=request.starter,
                fuel_system=request.fuel_system,
                engine_displacement=request.engine_displacement,
                cooling=request.cooling,
                style=request.style,
                engine_type=request.engine_type,
                gears=request.gears,
                front_rear_brake=request.front_rear_brake
            )
            
            # Atualizar no repositório
            updated_motorcycle = await self.motorcycle_repository.update_motorcycle(motorcycle_id, motor_vehicle, motorcycle)
            if not updated_motorcycle:
                logger.info(f"Moto não encontrada para atualização. ID: {motorcycle_id}")
                return None
            
            response = self._motorcycle_to_response(updated_motorcycle)
            logger.info(f"Moto atualizada com sucesso. ID: {motorcycle_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao atualizar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao atualizar moto: {str(e)}")
    
    async def delete_motorcycle(self, motorcycle_id: int) -> bool:
        """
        Remove uma moto.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            bool: True se removida com sucesso, False se não encontrada
        """
        try:
            logger.info(f"Removendo moto ID: {motorcycle_id}")
            
            result = await self.motorcycle_repository.delete_motorcycle(motorcycle_id)
            if result:
                logger.info(f"Moto removida com sucesso. ID: {motorcycle_id}")
            else:
                logger.info(f"Moto não encontrada para remoção. ID: {motorcycle_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao remover moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao remover moto: {str(e)}")
    
    async def inactivate_motorcycle(self, motorcycle_id: int) -> Optional[MotorcycleResponse]:
        """
        Inativa uma moto alterando seu status para 'Inativo'.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            Optional[MotorcycleResponse]: Dados da moto inativada ou None se não encontrada
        """
        try:
            logger.info(f"Inativando moto ID: {motorcycle_id}")
            
            # Buscar a moto atual
            current_motorcycle = await self.motorcycle_repository.get_motorcycle_by_id(motorcycle_id)
            if not current_motorcycle:
                logger.info(f"Moto não encontrada para inativação. ID: {motorcycle_id}")
                return None
            
            # Criar entidade motor_vehicle com status 'Inativo', mantendo os outros dados
            motor_vehicle = current_motorcycle.motor_vehicle
            motor_vehicle.status = 'Inativo'
            
            # Atualizar no repositório
            updated_motorcycle = await self.motorcycle_repository.update_motorcycle(motorcycle_id, motor_vehicle, current_motorcycle)
            if not updated_motorcycle:
                logger.info(f"Falha ao inativar moto. ID: {motorcycle_id}")
                return None
            
            response = self._motorcycle_to_response(updated_motorcycle)
            logger.info(f"Moto inativada com sucesso. ID: {motorcycle_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao inativar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao inativar moto: {str(e)}")
    
    async def activate_motorcycle(self, motorcycle_id: int) -> Optional[MotorcycleResponse]:
        """
        Ativa uma moto alterando seu status para 'Ativo'.
        
        Args:
            motorcycle_id: ID da moto
            
        Returns:
            Optional[MotorcycleResponse]: Dados da moto ativada ou None se não encontrada
        """
        try:
            logger.info(f"Ativando moto ID: {motorcycle_id}")
            
            # Buscar a moto atual
            current_motorcycle = await self.motorcycle_repository.get_motorcycle_by_id(motorcycle_id)
            if not current_motorcycle:
                logger.info(f"Moto não encontrada para ativação. ID: {motorcycle_id}")
                return None
            
            # Criar entidade motor_vehicle com status 'Ativo', mantendo os outros dados
            motor_vehicle = current_motorcycle.motor_vehicle
            motor_vehicle.status = 'Ativo'
            
            # Atualizar no repositório
            updated_motorcycle = await self.motorcycle_repository.update_motorcycle(motorcycle_id, motor_vehicle, current_motorcycle)
            if not updated_motorcycle:
                logger.info(f"Falha ao ativar moto. ID: {motorcycle_id}")
                return None
            
            response = self._motorcycle_to_response(updated_motorcycle)
            logger.info(f"Moto ativada com sucesso. ID: {motorcycle_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao ativar moto ID {motorcycle_id}: {str(e)}")
            raise Exception(f"Erro ao ativar moto: {str(e)}")
    
    async def get_active_motorcycles_by_price(self) -> List[MotorcycleResponse]:
        """
        Busca todas as motos com status 'Ativo' ordenadas por preço (menor para maior).
        
        Returns:
            List[MotorcycleResponse]: Lista de motos ativas ordenadas por preço
        """
        try:
            logger.info("Buscando motos ativas ordenadas por preço")
            
            motorcycles = await self.motorcycle_repository.get_active_motorcycles_by_price()
            
            # Converter para DTOs de resposta
            responses = [self._motorcycle_to_response(motorcycle) for motorcycle in motorcycles]
            
            logger.info(f"Encontradas {len(responses)} motos ativas")
            return responses
            
        except Exception as e:
            logger.error(f"Erro ao buscar motos ativas por preço: {str(e)}")
            raise Exception(f"Erro ao buscar motos ativas: {str(e)}")
    
    def _motorcycle_to_response(self, motorcycle: Motorcycle) -> MotorcycleResponse:
        """
        Converte uma entidade Motorcycle para MotorcycleResponse.
        
        Args:
            motorcycle: Entidade do domínio
            
        Returns:
            MotorcycleResponse: DTO de resposta
        """
        motor_vehicle = motorcycle.motor_vehicle
        
        return MotorcycleResponse(
            id=motor_vehicle.id,
            model=motor_vehicle.model,
            year=motor_vehicle.year,
            mileage=motor_vehicle.mileage,
            fuel_type=motor_vehicle.fuel_type,
            color=motor_vehicle.color,
            city=motor_vehicle.city,
            price=motor_vehicle.price,
            additional_description=motor_vehicle.additional_description,
            status=motor_vehicle.status,
            starter=motorcycle.starter,
            fuel_system=motorcycle.fuel_system,
            engine_displacement=motorcycle.engine_displacement,
            cooling=motorcycle.cooling,
            style=motorcycle.style,
            engine_type=motorcycle.engine_type,
            gears=motorcycle.gears,
            front_rear_brake=motorcycle.front_rear_brake,
            created_at=motor_vehicle.created_at.isoformat() if motor_vehicle.created_at else "",
            updated_at=motor_vehicle.updated_at.isoformat() if motor_vehicle.updated_at else ""
        )
