from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, BIGINT
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from typing import Optional
from datetime import datetime


class User(Base):
    """
    Entidade User que representa a tabela users no banco de dados.
    """
    __tablename__ = 'users'

    # Roles possíveis para usuários
    ROLE_VENDEDOR = "Vendedor"
    ROLE_ADMINISTRADOR = "Administrador"
    
    VALID_ROLES = [ROLE_VENDEDOR, ROLE_ADMINISTRADOR]

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Hash da senha
    role = Column(String(50), nullable=False)
    employee_id = Column(BIGINT, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamentos
    employee = relationship("Employee", backref="user", uselist=False)

    def __init__(self, email: str, password: str, role: str, employee_id: Optional[int] = None):
        self.email = email
        self.password = password
        self.role = role
        self.employee_id = employee_id

    @classmethod
    def create_user(cls, email: str, password_hash: str, role: str, employee_id: Optional[int] = None):
        """
        Método de classe para criar um usuário.
        
        Args:
            email: Email do usuário
            password_hash: Hash da senha
            role: Role do usuário (Vendedor ou Administrador)
            employee_id: ID do funcionário associado (opcional)
        """
        if role not in cls.VALID_ROLES:
            raise ValueError(f"Role inválida. Deve ser uma de: {', '.join(cls.VALID_ROLES)}")
        
        return cls(
            email=email,
            password=password_hash,
            role=role,
            employee_id=employee_id
        )

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Verifica se a role é válida"""
        return role in cls.VALID_ROLES

    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.role == self.ROLE_ADMINISTRADOR

    def is_vendedor(self) -> bool:
        """Verifica se o usuário é vendedor"""
        return self.role == self.ROLE_VENDEDOR

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
