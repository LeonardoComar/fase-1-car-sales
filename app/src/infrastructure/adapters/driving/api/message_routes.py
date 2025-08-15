from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.src.application.services.message_service import MessageService
from app.src.application.dtos.message_dto import (
    MessageCreateRequest,
    MessageStartServiceRequest, 
    MessageUpdateStatusRequest,
    MessageResponse,
    MessagesListResponse,
    MessageCreatedResponse,
    MessageStatus
)
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.message_repository_impl import MessageRepositoryImpl
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_or_vendedor_user
)

router = APIRouter(prefix="/messages", tags=["Messages"])

def get_message_service() -> MessageService:
    """Dependency injection para o serviço de mensagens"""
    message_repository = MessageRepositoryImpl()
    return MessageService(message_repository)

@router.post("/", response_model=MessageCreatedResponse, status_code=201)
async def create_message(
    request: MessageCreateRequest,
    message_service: MessageService = Depends(get_message_service)
):
    """
    Criar uma nova mensagem.
    
    Status inicial: "Pendente"
    responsible_id e service_start_time: não preenchidos na criação
    """
    try:
        return message_service.create_message(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=MessagesListResponse)
async def list_messages(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    responsible_id: Optional[int] = Query(None, description="Filtrar por ID do responsável"),
    vehicle_id: Optional[int] = Query(None, description="Filtrar por ID do veículo"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Listar mensagens com filtros opcionais.
    
    Requer autenticação: Administrador ou Vendedor
    
    Filtros disponíveis:
    - status: Filtrar por status da mensagem
    - responsible_id: Filtrar por funcionário responsável
    - vehicle_id: Filtrar por veículo relacionado
    """
    try:
        return message_service.get_messages_with_filters(
            status=status,
            responsible_id=responsible_id,
            vehicle_id=vehicle_id,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{message_id}/start-service", response_model=MessageResponse)
async def start_service(
    message_id: int,
    request: MessageStartServiceRequest,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Iniciar atendimento de uma mensagem.
    
    Requer autenticação: Administrador ou Vendedor
    
    Ações realizadas:
    - Atribui responsible_id
    - Define service_start_time com horário atual
    - Atualiza status para "Contato iniciado"
    """
    try:
        return message_service.start_service(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{message_id}/status", response_model=MessageResponse)
async def update_status(
    message_id: int,
    request: MessageUpdateStatusRequest,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Atualizar status de uma mensagem.
    
    Requer autenticação: Administrador ou Vendedor
    
    Status disponíveis:
    - Pendente
    - Contato iniciado  
    - Finalizado
    - Cancelado
    """
    try:
        return message_service.update_status(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Buscar mensagem por ID
    
    Requer autenticação: Administrador ou Vendedor
    """
    try:
        return message_service.get_message_by_id(message_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rotas específicas para atualização de status (seguindo padrão do sistema)
@router.patch("/{message_id}/pending", response_model=MessageResponse)
async def set_pending_status(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """Definir status como 'Pendente' - Requer autenticação: Administrador ou Vendedor"""
    request = MessageUpdateStatusRequest(status=MessageStatus.PENDING)
    try:
        return message_service.update_status(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{message_id}/contact-initiated", response_model=MessageResponse)
async def set_contact_initiated_status(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """Definir status como 'Contato iniciado' - Requer autenticação: Administrador ou Vendedor"""
    request = MessageUpdateStatusRequest(status=MessageStatus.CONTACT_INITIATED)
    try:
        return message_service.update_status(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{message_id}/finished", response_model=MessageResponse)
async def set_finished_status(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """Definir status como 'Finalizado' - Requer autenticação: Administrador ou Vendedor"""
    request = MessageUpdateStatusRequest(status=MessageStatus.FINISHED)
    try:
        return message_service.update_status(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{message_id}/cancelled", response_model=MessageResponse)
async def set_cancelled_status(
    message_id: int,
    message_service: MessageService = Depends(get_message_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """Definir status como 'Cancelado' - Requer autenticação: Administrador ou Vendedor"""
    request = MessageUpdateStatusRequest(status=MessageStatus.CANCELLED)
    try:
        return message_service.update_status(message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
