from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from typing import Optional


class Employee(Base):
    """
    Entidade Employee que representa a tabela employees no banco de dados.
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    cpf = Column(String(14), nullable=False)
    status = Column(String(50), nullable=False)
    address_id = Column(Integer, ForeignKey('addresses.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamento com Address (importando da entidade client_model)
    address = relationship("Address", backref="employees", uselist=False)

    def __init__(self, name: str, email: str, cpf: str, phone: Optional[str] = None, 
                 status: str = "Ativo", address_id: Optional[int] = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.cpf = cpf
        self.status = status
        self.address_id = address_id

    @classmethod
    def create_with_address(cls, name: str, email: str, cpf: str, phone: Optional[str] = None,
                           street: Optional[str] = None, city: Optional[str] = None,
                           state: Optional[str] = None, zip_code: Optional[str] = None,
                           country: Optional[str] = None):
        """
        Método de classe para criar um funcionário com endereço.
        """
        from app.src.domain.entities.client_model import Address
        
        address = None
        if any([street, city, state, zip_code, country]):
            address = Address(
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
                country=country
            )
        
        employee = cls(
            name=name,
            email=email,
            cpf=cpf,
            phone=phone,
            status="Ativo",  # Status padrão sempre "Ativo"
            address_id=0  # Será definido após a inserção do address
        )
        
        return address, employee

    def update_fields(self, name: Optional[str] = None, email: Optional[str] = None,
                     phone: Optional[str] = None, cpf: Optional[str] = None,
                     status: Optional[str] = None):
        """
        Atualiza os campos do funcionário.
        """
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if cpf is not None:
            self.cpf = cpf
        if status is not None:
            self.status = status

    def activate(self):
        """
        Ativa o funcionário.
        """
        self.status = "Ativo"

    def deactivate(self):
        """
        Desativa o funcionário.
        """
        self.status = "Inativo"

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', email='{self.email}', status='{self.status}')>"
