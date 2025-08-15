from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.src.domain.entities.user_model import User
from app.src.domain.ports.user_repository import UserRepositoryInterface
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class UserRepositoryImpl(UserRepositoryInterface):
    """
    Implementação concreta do repositório de usuários.
    Adaptador que implementa a interface definida no domínio.
    """
    
    def __init__(self):
        pass
    
    async def create_user(self, user: User) -> User:
        """
        Cria um novo usuário no banco de dados.
        """
        try:
            with get_db_session() as session:
                session.add(user)
                session.commit()
                session.refresh(user)
                
                # Fazer expunge para desconectar o objeto da sessão
                session.expunge(user)
                
                logger.info(f"Usuário criado com sucesso. ID: {user.id}, Email: {user.email}")
                return user
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise Exception(f"Erro ao criar usuário: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar usuário: {str(e)}")
            raise Exception(f"Erro inesperado ao criar usuário: {str(e)}")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca um usuário pelo ID.
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    # Fazer expunge para desconectar o objeto da sessão
                    session.expunge(user)
                    
                return user
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar usuário por ID {user_id}: {str(e)}")
            raise Exception(f"Erro ao buscar usuário: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar usuário por ID {user_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar usuário: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca um usuário pelo email.
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.email == email).first()
                if user:
                    # Fazer expunge para desconectar o objeto da sessão
                    session.expunge(user)
                    
                return user
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar usuário por email {email}: {str(e)}")
            raise Exception(f"Erro ao buscar usuário: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar usuário por email {email}: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar usuário: {str(e)}")
    
    async def update_user(self, user_id: int, user: User) -> Optional[User]:
        """
        Atualiza um usuário existente.
        """
        try:
            with get_db_session() as session:
                existing_user = session.query(User).filter(User.id == user_id).first()
                
                if not existing_user:
                    return None
                
                # Atualizar campos
                existing_user.email = user.email
                existing_user.password = user.password
                existing_user.role = user.role
                existing_user.employee_id = user.employee_id
                
                session.commit()
                session.refresh(existing_user)
                
                # Fazer expunge para desconectar o objeto da sessão
                session.expunge(existing_user)
                
                logger.info(f"Usuário atualizado com sucesso. ID: {user_id}")
                return existing_user
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar usuário ID {user_id}: {str(e)}")
            raise Exception(f"Erro ao atualizar usuário: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar usuário ID {user_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao atualizar usuário: {str(e)}")
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Remove um usuário do banco de dados.
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                session.delete(user)
                session.commit()
                
                logger.info(f"Usuário deletado com sucesso. ID: {user_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao deletar usuário ID {user_id}: {str(e)}")
            raise Exception(f"Erro ao deletar usuário: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar usuário ID {user_id}: {str(e)}")
            raise Exception(f"Erro inesperado ao deletar usuário: {str(e)}")
