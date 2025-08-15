from sqlalchemy import Column, String, TIMESTAMP, func, BIGINT
from app.src.infrastructure.driven.database.connection_mysql import Base
from datetime import datetime
from typing import Optional


class BlacklistedToken(Base):
    """
    Entidade BlacklistedToken que representa tokens invalidados (logout).
    """
    __tablename__ = 'blacklisted_tokens'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    jti = Column(String(255), nullable=False, unique=True, index=True)  # JWT ID
    token = Column(String(1000), nullable=False)  # Token completo (para referência)
    user_id = Column(BIGINT, nullable=False, index=True)
    blacklisted_at = Column(TIMESTAMP, default=func.current_timestamp())
    expires_at = Column(TIMESTAMP, nullable=False)  # Quando o token expira naturalmente

    def __init__(self, jti: str, token: str, user_id: int, expires_at: datetime):
        self.jti = jti
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at

    @classmethod
    def create_blacklisted_token(cls, jti: str, token: str, user_id: int, expires_at: datetime):
        """
        Método de classe para criar um token blacklisted.
        
        Args:
            jti: JWT ID único
            token: Token JWT completo
            user_id: ID do usuário
            expires_at: Data de expiração do token
        """
        return cls(
            jti=jti,
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )

    def __repr__(self):
        return f"<BlacklistedToken(jti='{self.jti}', user_id={self.user_id})>"
