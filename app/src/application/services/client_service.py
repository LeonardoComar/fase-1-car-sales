from typing import Optional, List
from app.src.domain.ports.client_repository import ClientRepositoryInterface
from app.src.domain.entities.client_model import Client, Address
from app.src.application.dtos.client_dto import CreateClientRequest, UpdateClientRequest, ClientResponse, ClientListResponse, AddressResponse
import logging

logger = logging.getLogger(__name__)


class ClientService:
    """
    Serviço de aplicação para operações relacionadas a clientes.
    Coordena as operações entre a camada de apresentação e o domínio.
    """
    
    def __init__(self, client_repository: ClientRepositoryInterface):
        self.client_repository = client_repository
    
    async def create_client(self, request: CreateClientRequest) -> ClientResponse:
        """
        Cria um novo cliente.
        
        Args:
            request: Dados para criação do cliente
            
        Returns:
            ClientResponse: Dados do cliente criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Iniciando criação de cliente: {request.name}")
            
            # Verificar se já existe cliente com mesmo email
            existing_client = await self.client_repository.get_client_by_email(request.email)
            if existing_client:
                raise ValueError(f"Já existe um cliente cadastrado com o email: {request.email}")
            
            # Verificar se já existe cliente com mesmo CPF
            existing_client_cpf = await self.client_repository.get_client_by_cpf(request.cpf)
            if existing_client_cpf:
                raise ValueError(f"Já existe um cliente cadastrado com o CPF: {request.cpf}")
            
            # Criar entidades do domínio
            address, client = Client.create_with_address(
                name=request.name,
                email=request.email,
                cpf=request.cpf,
                phone=request.phone,
                street=request.street,
                city=request.city,
                state=request.state,
                zip_code=request.zip_code,
                country=request.country
            )
            
            # Persistir no repositório
            created_client = await self.client_repository.create_client(address, client)
            
            logger.info(f"Cliente criado com sucesso. ID: {created_client.id}")
            
            # Converter para DTO de resposta
            return self._convert_to_client_response(created_client)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao criar cliente: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao criar cliente: {e}")
            raise Exception(f"Erro interno do servidor ao criar cliente: {str(e)}")
    
    async def get_client_by_id(self, client_id: int) -> Optional[ClientResponse]:
        """
        Busca um cliente pelo ID.
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Optional[ClientResponse]: Dados do cliente ou None se não encontrado
        """
        try:
            logger.info(f"Buscando cliente por ID: {client_id}")
            
            client = await self.client_repository.get_client_by_id(client_id)
            
            if not client:
                logger.warning(f"Cliente não encontrado com ID: {client_id}")
                return None
            
            logger.info(f"Cliente encontrado: {client.name}")
            return self._convert_to_client_response(client)
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID {client_id}: {e}")
            raise Exception(f"Erro interno do servidor ao buscar cliente: {str(e)}")
    
    async def get_client_by_cpf(self, cpf: str) -> Optional[ClientResponse]:
        """
        Busca um cliente pelo CPF.
        
        Args:
            cpf: CPF do cliente
            
        Returns:
            Optional[ClientResponse]: Dados do cliente ou None se não encontrado
        """
        try:
            logger.info(f"Buscando cliente por CPF: {cpf}")
            
            client = await self.client_repository.get_client_by_cpf(cpf)
            
            if not client:
                logger.warning(f"Cliente não encontrado com CPF: {cpf}")
                return None
            
            logger.info(f"Cliente encontrado: {client.name}")
            return self._convert_to_client_response(client)
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF {cpf}: {e}")
            raise Exception(f"Erro interno do servidor ao buscar cliente: {str(e)}")
    
    async def update_client(self, client_id: int, request: UpdateClientRequest) -> Optional[ClientResponse]:
        """
        Atualiza um cliente existente.
        
        Args:
            client_id: ID do cliente
            request: Dados para atualização
            
        Returns:
            Optional[ClientResponse]: Dados do cliente atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        try:
            logger.info(f"Iniciando atualização de cliente. ID: {client_id}")
            
            # Verificar se o cliente existe
            existing_client = await self.client_repository.get_client_by_id(client_id)
            if not existing_client:
                logger.warning(f"Cliente não encontrado para atualização. ID: {client_id}")
                return None
            
            # Verificar se email está sendo alterado e se já existe
            if request.email and request.email != existing_client.email:
                email_client = await self.client_repository.get_client_by_email(request.email)
                if email_client and email_client.id != client_id:
                    raise ValueError(f"Já existe outro cliente cadastrado com o email: {request.email}")
            
            # Verificar se CPF está sendo alterado e se já existe
            if request.cpf and request.cpf != existing_client.cpf:
                cpf_client = await self.client_repository.get_client_by_cpf(request.cpf)
                if cpf_client and cpf_client.id != client_id:
                    raise ValueError(f"Já existe outro cliente cadastrado com o CPF: {request.cpf}")
            
            # Criar entidades atualizadas
            address = None
            if any([request.street, request.city, request.state, request.zip_code, request.country]):
                address = Address(
                    street=request.street,
                    city=request.city,
                    state=request.state,
                    zip_code=request.zip_code,
                    country=request.country
                )
                if existing_client.address_id:
                    address.id = existing_client.address_id
            
            # Atualizar dados do cliente
            client = Client(
                name=request.name or existing_client.name,
                email=request.email or existing_client.email,
                cpf=request.cpf or existing_client.cpf,
                phone=request.phone if request.phone is not None else existing_client.phone,
                address_id=existing_client.address_id
            )
            client.id = client_id
            
            # Persistir no repositório
            updated_client = await self.client_repository.update_client(client_id, address, client)
            
            if not updated_client:
                logger.warning(f"Falha ao atualizar cliente. ID: {client_id}")
                return None
            
            logger.info(f"Cliente atualizado com sucesso. ID: {client_id}")
            return self._convert_to_client_response(updated_client)
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar cliente {client_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar cliente {client_id}: {e}")
            raise Exception(f"Erro interno do servidor ao atualizar cliente: {str(e)}")
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Remove um cliente.
        
        Args:
            client_id: ID do cliente
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        try:
            logger.info(f"Iniciando remoção de cliente. ID: {client_id}")
            
            success = await self.client_repository.delete_client(client_id)
            
            if success:
                logger.info(f"Cliente removido com sucesso. ID: {client_id}")
            else:
                logger.warning(f"Cliente não encontrado para remoção. ID: {client_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover cliente {client_id}: {e}")
            raise Exception(f"Erro interno do servidor ao remover cliente: {str(e)}")
    
    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[ClientListResponse]:
        """
        Lista todos os clientes com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[ClientListResponse]: Lista de clientes
        """
        try:
            logger.info(f"Listando clientes. Skip: {skip}, Limit: {limit}")
            
            clients = await self.client_repository.get_all_clients(skip, limit)
            
            logger.info(f"Encontrados {len(clients)} clientes")
            
            return [self._convert_to_client_list_response(client) for client in clients]
            
        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}")
            raise Exception(f"Erro interno do servidor ao listar clientes: {str(e)}")
    
    async def search_clients_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[ClientListResponse]:
        """
        Busca clientes por nome.
        
        Args:
            name: Nome ou parte do nome para buscar
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[ClientListResponse]: Lista de clientes encontrados
        """
        try:
            logger.info(f"Buscando clientes por nome: {name}")
            
            clients = await self.client_repository.search_clients_by_name(name, skip, limit)
            
            logger.info(f"Encontrados {len(clients)} clientes com nome '{name}'")
            
            return [self._convert_to_client_list_response(client) for client in clients]
            
        except Exception as e:
            logger.error(f"Erro ao buscar clientes por nome '{name}': {e}")
            raise Exception(f"Erro interno do servidor ao buscar clientes: {str(e)}")
    
    def _convert_to_client_response(self, client: Client) -> ClientResponse:
        """
        Converte uma entidade Client para ClientResponse.
        
        Args:
            client: Entidade do cliente
            
        Returns:
            ClientResponse: DTO de resposta do cliente
        """
        address_response = None
        if client.address:
            address_response = AddressResponse(
                id=client.address.id,
                street=client.address.street,
                city=client.address.city,
                state=client.address.state,
                zip_code=client.address.zip_code,
                country=client.address.country
            )
        
        return ClientResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            cpf=client.cpf,
            address=address_response,
            created_at=client.created_at.isoformat() if client.created_at else "",
            updated_at=client.updated_at.isoformat() if client.updated_at else ""
        )
    
    def _convert_to_client_list_response(self, client: Client) -> ClientListResponse:
        """
        Converte uma entidade Client para ClientListResponse.
        
        Args:
            client: Entidade do cliente
            
        Returns:
            ClientListResponse: DTO de resposta simplificada do cliente
        """
        city = None
        if client.address:
            city = client.address.city
        
        return ClientListResponse(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            cpf=client.cpf,
            city=city
        )
