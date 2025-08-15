from typing import List, Optional
from datetime import datetime
from app.src.domain.entities.message_model import Message, MessageStatus
from app.src.domain.ports.message_repository import MessageRepository
from app.src.application.dtos.message_dto import (
    MessageCreateRequest, 
    MessageStartServiceRequest, 
    MessageUpdateStatusRequest,
    MessageResponse,
    MessagesListResponse,
    MessageCreatedResponse
)

class MessageService:
    
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository
    
    def create_message(self, request: MessageCreateRequest) -> MessageCreatedResponse:
        """Criar uma nova mensagem"""
        message = Message(
            name=request.name,
            email=request.email,
            phone=request.phone,
            message=request.message,
            vehicle_id=request.vehicle_id,
            status=MessageStatus.PENDING.value,  # Status inicial definido no modelo
            responsible_id=None,  # Não preenchido na criação
            service_start_time=None  # Não preenchido na criação
        )
        
        created_message = self.message_repository.create(message)
        
        return MessageCreatedResponse(
            id=created_message.id,
            name=created_message.name,
            email=created_message.email,
            status=created_message.status,
            message=created_message.message,
            created_at=created_message.created_at
        )
    
    def get_messages_with_filters(
        self,
        status: Optional[str] = None,
        responsible_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        page: int = 1,
        limit: int = 10
    ) -> MessagesListResponse:
        """Buscar mensagens com filtros"""
        offset = (page - 1) * limit
        
        messages = self.message_repository.find_all_with_filters(
            status=status,
            responsible_id=responsible_id,
            vehicle_id=vehicle_id,
            limit=limit,
            offset=offset
        )
        
        total = self.message_repository.count_with_filters(
            status=status,
            responsible_id=responsible_id,
            vehicle_id=vehicle_id
        )
        
        total_pages = (total + limit - 1) // limit
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                responsible_id=msg.responsible_id,
                vehicle_id=msg.vehicle_id,
                name=msg.name,
                email=msg.email,
                phone=msg.phone,
                message=msg.message,
                status=msg.status,
                service_start_time=msg.service_start_time,
                created_at=msg.created_at,
                updated_at=msg.updated_at
            ) for msg in messages
        ]
        
        return MessagesListResponse(
            messages=message_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def start_service(self, message_id: int, request: MessageStartServiceRequest) -> MessageResponse:
        """Iniciar atendimento de uma mensagem"""
        message = self.message_repository.find_by_id(message_id)
        
        if not message:
            raise ValueError(f"Mensagem com ID {message_id} não encontrada")
        
        if message.responsible_id is not None:
            raise ValueError("Mensagem já possui responsável atribuído")
        
        # Usar update_by_id para evitar problemas de sessão
        updates = {
            'responsible_id': request.responsible_id,
            'service_start_time': datetime.utcnow(),
            'status': MessageStatus.CONTACT_INITIATED.value
        }
        
        updated_message = self.message_repository.update_by_id(message_id, updates)
        
        return MessageResponse(
            id=updated_message.id,
            responsible_id=updated_message.responsible_id,
            vehicle_id=updated_message.vehicle_id,
            name=updated_message.name,
            email=updated_message.email,
            phone=updated_message.phone,
            message=updated_message.message,
            status=updated_message.status,
            service_start_time=updated_message.service_start_time,
            created_at=updated_message.created_at,
            updated_at=updated_message.updated_at
        )
    
    def update_status(self, message_id: int, request: MessageUpdateStatusRequest) -> MessageResponse:
        """Atualizar status de uma mensagem"""
        message = self.message_repository.find_by_id(message_id)
        
        if not message:
            raise ValueError(f"Mensagem com ID {message_id} não encontrada")
        
        # Usar update_by_id para evitar problemas de sessão
        updates = {
            'status': request.status.value
        }
        
        updated_message = self.message_repository.update_by_id(message_id, updates)
        
        return MessageResponse(
            id=updated_message.id,
            responsible_id=updated_message.responsible_id,
            vehicle_id=updated_message.vehicle_id,
            name=updated_message.name,
            email=updated_message.email,
            phone=updated_message.phone,
            message=updated_message.message,
            status=updated_message.status,
            service_start_time=updated_message.service_start_time,
            created_at=updated_message.created_at,
            updated_at=updated_message.updated_at
        )
    
    def get_message_by_id(self, message_id: int) -> MessageResponse:
        """Buscar mensagem por ID"""
        message = self.message_repository.find_by_id(message_id)
        
        if not message:
            raise ValueError(f"Mensagem com ID {message_id} não encontrada")
        
        return MessageResponse(
            id=message.id,
            responsible_id=message.responsible_id,
            vehicle_id=message.vehicle_id,
            name=message.name,
            email=message.email,
            phone=message.phone,
            message=message.message,
            status=message.status,
            service_start_time=message.service_start_time,
            created_at=message.created_at,
            updated_at=message.updated_at
        )
