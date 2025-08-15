from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from app.src.domain.entities.blacklisted_token_model import BlacklistedToken
from app.src.domain.ports.blacklisted_token_repository import BlacklistedTokenRepositoryInterface
from app.src.infrastructure.driven.database.connection_mysql import get_db_session
import logging

logger = logging.getLogger(__name__)


class BlacklistedTokenRepositoryImpl(BlacklistedTokenRepositoryInterface):
    """
    Implementação concreta do repositório de tokens blacklisted.
    Adaptador que implementa a interface definida no domínio.
    """
    
    def __init__(self):
        pass
    
    async def add_token_to_blacklist(self, blacklisted_token: BlacklistedToken) -> BlacklistedToken:
        """
        Adiciona um token à blacklist.
        """
        try:
            with get_db_session() as session:
                session.add(blacklisted_token)
                session.commit()
                session.refresh(blacklisted_token)
                
                # Fazer expunge para desconectar o objeto da sessão
                session.expunge(blacklisted_token)
                
                logger.info(f"Token adicionado à blacklist. JTI: {blacklisted_token.jti}")
                return blacklisted_token
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao adicionar token à blacklist: {str(e)}")
            raise Exception(f"Erro ao adicionar token à blacklist: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao adicionar token à blacklist: {str(e)}")
            raise Exception(f"Erro inesperado ao adicionar token à blacklist: {str(e)}")
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Verifica se um token está na blacklist.
        """
        try:
            with get_db_session() as session:
                blacklisted_token = session.query(BlacklistedToken)\
                    .filter(BlacklistedToken.jti == jti)\
                    .first()
                
                return blacklisted_token is not None
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao verificar token na blacklist: {str(e)}")
            return False  # Em caso de erro, assumir que não está na blacklist
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar token na blacklist: {str(e)}")
            return False
    
    async def get_blacklisted_token_by_jti(self, jti: str) -> Optional[BlacklistedToken]:
        """
        Busca um token blacklisted pelo JTI.
        """
        try:
            with get_db_session() as session:
                blacklisted_token = session.query(BlacklistedToken)\
                    .filter(BlacklistedToken.jti == jti)\
                    .first()
                
                if blacklisted_token:
                    # Fazer expunge para desconectar o objeto da sessão
                    session.expunge(blacklisted_token)
                    
                return blacklisted_token
                
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar token blacklisted por JTI {jti}: {str(e)}")
            raise Exception(f"Erro ao buscar token blacklisted: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar token blacklisted por JTI {jti}: {str(e)}")
            raise Exception(f"Erro inesperado ao buscar token blacklisted: {str(e)}")
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Remove tokens expirados da blacklist para limpeza.
        """
        try:
            with get_db_session() as session:
                current_time = datetime.utcnow()
                
                # Buscar tokens expirados
                expired_tokens = session.query(BlacklistedToken)\
                    .filter(BlacklistedToken.expires_at < current_time)\
                    .all()
                
                count = len(expired_tokens)
                
                # Deletar tokens expirados
                if expired_tokens:
                    session.query(BlacklistedToken)\
                        .filter(BlacklistedToken.expires_at < current_time)\
                        .delete()
                    session.commit()
                
                logger.info(f"Limpeza de tokens expirados: {count} tokens removidos")
                return count
                
        except SQLAlchemyError as e:
            logger.error(f"Erro na limpeza de tokens expirados: {str(e)}")
            raise Exception(f"Erro na limpeza de tokens expirados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado na limpeza de tokens expirados: {str(e)}")
            raise Exception(f"Erro inesperado na limpeza de tokens expirados: {str(e)}")
