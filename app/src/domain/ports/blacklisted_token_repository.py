from abc import ABC, abstractmethod
from typing import Optional
from app.src.domain.entities.blacklisted_token_model import BlacklistedToken


class BlacklistedTokenRepositoryInterface(ABC):
    """
    Interface do repositório de tokens blacklisted.
    Define os métodos que devem ser implementados pelos adaptadores de persistência.
    """

    @abstractmethod
    async def add_token_to_blacklist(self, blacklisted_token: BlacklistedToken) -> BlacklistedToken:
        """
        Adiciona um token à blacklist.
        
        Args:
            blacklisted_token: Token a ser adicionado à blacklist
            
        Returns:
            BlacklistedToken: Token adicionado à blacklist
        """
        pass

    @abstractmethod
    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Verifica se um token está na blacklist.
        
        Args:
            jti: JWT ID para verificar
            
        Returns:
            bool: True se o token estiver na blacklist, False caso contrário
        """
        pass

    @abstractmethod
    async def get_blacklisted_token_by_jti(self, jti: str) -> Optional[BlacklistedToken]:
        """
        Busca um token blacklisted pelo JTI.
        
        Args:
            jti: JWT ID para buscar
            
        Returns:
            Optional[BlacklistedToken]: Token encontrado ou None
        """
        pass

    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """
        Remove tokens expirados da blacklist para limpeza.
        
        Returns:
            int: Número de tokens removidos
        """
        pass
