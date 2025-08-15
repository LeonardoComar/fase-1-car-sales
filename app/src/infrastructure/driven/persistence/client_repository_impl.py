from typing import Optional, List
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.src.domain.ports.client_repository import ClientRepositoryInterface
from app.src.domain.entities.client_model import Client, Address
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class ClientRepository(ClientRepositoryInterface):
    """
    Implementação do repositório de clientes usando SQLAlchemy.
    """
    
    def __init__(self):
        pass
    
    async def create_client(self, address: Optional[Address], client: Client) -> Client:
        """
        Cria um novo cliente no banco de dados.
        
        Args:
            address: Dados do endereço (opcional)
            client: Dados do cliente
            
        Returns:
            Client: O cliente criado com ID gerado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            logger.info(f"Criando cliente no banco: {client.name}")
            
            with get_db_session() as session:
                # Criar endereço se fornecido
                if address:
                    session.add(address)
                    session.flush()  # Para obter o ID do endereço
                    client.address_id = address.id
                    logger.info(f"Endereço criado com ID: {address.id}")
                
                # Criar cliente
                session.add(client)
                session.commit()
                
                # Recarregar para ter os relacionamentos
                session.refresh(client)
                if client.address_id:
                    client.address = session.get(Address, client.address_id)
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(client)
                if client.address:
                    session.expunge(client.address)
                
                logger.info(f"Cliente criado com sucesso. ID: {client.id}")
                return client
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao criar cliente: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar cliente: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """
        Busca um cliente pelo ID.
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        try:
            logger.info(f"Buscando cliente por ID: {client_id}")
            
            with get_db_session() as session:
                client = session.query(Client).options(joinedload(Client.address)).filter(Client.id == client_id).first()
                
                if client:
                    logger.info(f"Cliente encontrado: {client.name}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(client)
                    if client.address:
                        session.expunge(client.address)
                else:
                    logger.info(f"Cliente não encontrado com ID: {client_id}")
                
                return client
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar cliente por ID {client_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar cliente por ID {client_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def update_client(self, client_id: int, address: Optional[Address], client: Client) -> Optional[Client]:
        """
        Atualiza um cliente existente.
        
        Args:
            client_id: ID do cliente
            address: Dados atualizados do endereço (opcional)
            client: Dados atualizados do cliente
            
        Returns:
            Optional[Client]: O cliente atualizado ou None se não encontrado
            
        Raises:
            Exception: Se houver erro na atualização
        """
        try:
            logger.info(f"Atualizando cliente ID: {client_id}")
            
            with get_db_session() as session:
                # Buscar cliente existente
                existing_client = session.query(Client).filter(Client.id == client_id).first()
                if not existing_client:
                    logger.warning(f"Cliente não encontrado para atualização. ID: {client_id}")
                    return None
                
                # Atualizar endereço se fornecido
                if address:
                    if existing_client.address_id:
                        # Atualizar endereço existente
                        existing_address = session.get(Address, existing_client.address_id)
                        if existing_address:
                            existing_address.street = address.street
                            existing_address.city = address.city
                            existing_address.state = address.state
                            existing_address.zip_code = address.zip_code
                            existing_address.country = address.country
                            logger.info(f"Endereço atualizado. ID: {existing_address.id}")
                    else:
                        # Criar novo endereço
                        session.add(address)
                        session.flush()
                        existing_client.address_id = address.id
                        logger.info(f"Novo endereço criado. ID: {address.id}")
                
                # Atualizar dados do cliente
                existing_client.name = client.name
                existing_client.email = client.email
                existing_client.phone = client.phone
                existing_client.cpf = client.cpf
                
                session.commit()
                
                # Recarregar para ter os relacionamentos atualizados
                session.refresh(existing_client)
                if existing_client.address_id:
                    existing_client.address = session.get(Address, existing_client.address_id)
                
                # Fazer expunge para desconectar os objetos da sessão
                session.expunge(existing_client)
                if existing_client.address:
                    session.expunge(existing_client.address)
                
                logger.info(f"Cliente atualizado com sucesso. ID: {client_id}")
                return existing_client
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao atualizar cliente {client_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar cliente {client_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Remove um cliente do banco de dados.
        
        Args:
            client_id: ID do cliente a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            Exception: Se houver erro na remoção
        """
        try:
            logger.info(f"Removendo cliente ID: {client_id}")
            
            with get_db_session() as session:
                # Buscar cliente
                client = session.query(Client).filter(Client.id == client_id).first()
                if not client:
                    logger.warning(f"Cliente não encontrado para remoção. ID: {client_id}")
                    return False
                
                # Remover cliente (o endereço será mantido devido ao ON DELETE SET NULL)
                session.delete(client)
                session.commit()
                
                logger.info(f"Cliente removido com sucesso. ID: {client_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao remover cliente {client_id}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao remover cliente {client_id}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_all_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Busca todos os clientes com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            logger.info(f"Buscando todos os clientes. Skip: {skip}, Limit: {limit}")
            
            with get_db_session() as session:
                clients = (session.query(Client)
                          .options(joinedload(Client.address))
                          .offset(skip)
                          .limit(limit)
                          .all())
                
                # Fazer expunge para desconectar os objetos da sessão
                for client in clients:
                    session.expunge(client)
                    if client.address:
                        session.expunge(client.address)
                
                logger.info(f"Encontrados {len(clients)} clientes")
                return clients
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar todos os clientes: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar todos os clientes: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """
        Busca um cliente pelo email.
        
        Args:
            email: Email do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        try:
            logger.info(f"Buscando cliente por email: {email}")
            
            with get_db_session() as session:
                client = session.query(Client).options(joinedload(Client.address)).filter(Client.email == email).first()
                
                if client:
                    logger.info(f"Cliente encontrado com email: {email}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(client)
                    if client.address:
                        session.expunge(client.address)
                else:
                    logger.info(f"Cliente não encontrado com email: {email}")
                
                return client
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar cliente por email {email}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar cliente por email {email}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def get_client_by_cpf(self, cpf: str) -> Optional[Client]:
        """
        Busca um cliente pelo CPF.
        
        Args:
            cpf: CPF do cliente
            
        Returns:
            Optional[Client]: O cliente encontrado ou None
        """
        try:
            logger.info(f"Buscando cliente por CPF: {cpf}")
            
            with get_db_session() as session:
                client = session.query(Client).options(joinedload(Client.address)).filter(Client.cpf == cpf).first()
                
                if client:
                    logger.info(f"Cliente encontrado com CPF: {cpf}")
                    # Fazer expunge para desconectar os objetos da sessão
                    session.expunge(client)
                    if client.address:
                        session.expunge(client.address)
                else:
                    logger.info(f"Cliente não encontrado com CPF: {cpf}")
                
                return client
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar cliente por CPF {cpf}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar cliente por CPF {cpf}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
    
    async def search_clients_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """
        Busca clientes por nome (busca parcial).
        
        Args:
            name: Nome ou parte do nome para buscar
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            List[Client]: Lista de clientes encontrados
        """
        try:
            logger.info(f"Buscando clientes por nome: {name}")
            
            with get_db_session() as session:
                clients = (session.query(Client)
                          .options(joinedload(Client.address))
                          .filter(Client.name.contains(name))
                          .offset(skip)
                          .limit(limit)
                          .all())
                
                # Fazer expunge para desconectar os objetos da sessão
                for client in clients:
                    session.expunge(client)
                    if client.address:
                        session.expunge(client.address)
                
                logger.info(f"Encontrados {len(clients)} clientes com nome contendo '{name}'")
                return clients
                
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco ao buscar clientes por nome {name}: {e}")
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar clientes por nome {name}: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")
