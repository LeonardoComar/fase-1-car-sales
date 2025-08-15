from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.src.application.services.client_service import ClientService
from app.src.application.dtos.client_dto import CreateClientRequest, UpdateClientRequest, ClientResponse, ClientListResponse
from app.src.application.dtos.user_dto import UserResponseDto
from app.src.infrastructure.driven.persistence.client_repository_impl import ClientRepository
from app.src.infrastructure.adapters.driving.api.auth_dependencies import (
    get_current_admin_or_vendedor_user
)
import logging

logger = logging.getLogger(__name__)

# Criar instâncias dos serviços
client_repository = ClientRepository()
client_service = ClientService(client_repository)

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_client_service() -> ClientService:
    """
    Dependency injection para o serviço de clientes.
    """
    return client_service


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    request: CreateClientRequest,
    service: ClientService = Depends(get_client_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> ClientResponse:
    """
    Cria um novo cliente.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        request: Dados do cliente a ser criado
        service: Serviço de clientes (injetado)
        current_user: Usuário autenticado
        
    Returns:
        ClientResponse: Dados do cliente criado
        
    Raises:
        HTTPException: 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para criar cliente: {request.name}")
        
        client_response = await service.create_client(request)
        
        logger.info(f"Cliente criado com sucesso via API. ID: {client_response.id}")
        return client_response
        
    except ValueError as e:
        logger.error(f"Erro de validação ao criar cliente via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro interno ao criar cliente via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client_by_id(
    client_id: int,
    service: ClientService = Depends(get_client_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> ClientResponse:
    """
    Busca um cliente pelo ID.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        client_id: ID do cliente
        service: Serviço de clientes (injetado)
        current_user: Usuário autenticado
        
    Returns:
        ClientResponse: Dados do cliente
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para buscar cliente por ID: {client_id}")
        
        client = await service.get_client_by_id(client_id)
        
        if not client:
            logger.warning(f"Cliente não encontrado via API. ID: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente com ID {client_id} não encontrado"
            )
        
        logger.info(f"Cliente encontrado via API. ID: {client_id}")
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao buscar cliente por ID via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    request: UpdateClientRequest,
    service: ClientService = Depends(get_client_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> ClientResponse:
    """
    Atualiza um cliente existente.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        client_id: ID do cliente
        request: Novos dados do cliente
        service: Serviço de clientes (injetado)
        current_user: Usuário autenticado
        
    Returns:
        ClientResponse: Dados do cliente atualizado
        
    Raises:
        HTTPException: 404 se não encontrado, 400 se dados inválidos, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para atualizar cliente ID: {client_id}")
        
        client = await service.update_client(client_id, request)
        
        if not client:
            logger.warning(f"Cliente não encontrado para atualização via API. ID: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente com ID {client_id} não encontrado"
            )
        
        logger.info(f"Cliente atualizado com sucesso via API. ID: {client_id}")
        return client
        
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar cliente via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao atualizar cliente via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    service: ClientService = Depends(get_client_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
):
    """
    Remove um cliente.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        client_id: ID do cliente
        service: Serviço de clientes (injetado)
        current_user: Usuário autenticado
        
    Raises:
        HTTPException: 404 se não encontrado, 500 se erro interno
    """
    try:
        logger.info(f"Recebida requisição para remover cliente ID: {client_id}")
        
        success = await service.delete_client(client_id)
        
        if not success:
            logger.warning(f"Cliente não encontrado para remoção via API. ID: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente com ID {client_id} não encontrado"
            )
        
        logger.info(f"Cliente removido com sucesso via API. ID: {client_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao remover cliente via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/", response_model=List[ClientListResponse])
async def get_all_clients(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros para retornar"),
    name: Optional[str] = Query(None, min_length=1, description="Nome ou parte do nome para filtrar (opcional)"),
    cpf: Optional[str] = Query(None, min_length=11, max_length=14, description="CPF para filtrar (opcional)"),
    service: ClientService = Depends(get_client_service),
    current_user: UserResponseDto = Depends(get_current_admin_or_vendedor_user)
) -> List[ClientListResponse]:
    """
    Lista todos os clientes com paginação e filtros opcionais por nome ou CPF.
    
    Requer autenticação: Administrador ou Vendedor
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros para retornar
        name: Nome ou parte do nome para filtrar (opcional)
        cpf: CPF para filtrar (opcional)
        service: Serviço de clientes (injetado)
        current_user: Usuário autenticado
        
    Returns:
        List[ClientListResponse]: Lista de clientes
        
    Raises:
        HTTPException: 400 se ambos os filtros forem fornecidos, 500 se erro interno
    """
    try:
        # Validar que apenas um filtro foi fornecido
        if name and cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça apenas um filtro por vez: 'name' ou 'cpf'"
            )
        
        if cpf:
            logger.info(f"Recebida requisição para buscar cliente por CPF: {cpf}")
            # Buscar por CPF retorna um único cliente ou None
            client = await service.get_client_by_cpf(cpf)
            if client:
                # Converter ClientResponse para ClientListResponse
                client_list = [{
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone": client.phone,
                    "cpf": client.cpf,
                    "city": client.address.city if client.address else None
                }]
                logger.info(f"Cliente encontrado por CPF via API")
                return client_list
            else:
                logger.info(f"Nenhum cliente encontrado com CPF: {cpf}")
                return []
        elif name:
            logger.info(f"Recebida requisição para buscar clientes por nome: {name}. Skip: {skip}, Limit: {limit}")
            clients = await service.search_clients_by_name(name, skip, limit)
            logger.info(f"Busca de clientes por nome realizada via API. Total: {len(clients)}")
            return clients
        else:
            logger.info(f"Recebida requisição para listar todos os clientes. Skip: {skip}, Limit: {limit}")
            clients = await service.get_all_clients(skip, limit)
            logger.info(f"Listagem de clientes realizada via API. Total: {len(clients)}")
            return clients
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao listar/buscar clientes via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
