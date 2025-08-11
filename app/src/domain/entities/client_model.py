from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from typing import Optional


class Address(Base):
    """
    Entidade Address que representa a tabela addresses no banco de dados.
    """
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __init__(self, street: Optional[str] = None, city: Optional[str] = None, 
                 state: Optional[str] = None, zip_code: Optional[str] = None, 
                 country: Optional[str] = None):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return f"<Address(id={self.id}, street='{self.street}', city='{self.city}')>"


class Client(Base):
    """
    Entidade Client que representa a tabela clients no banco de dados.
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    cpf = Column(String(14), nullable=False)
    address_id = Column(Integer, ForeignKey('addresses.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamento com Address
    address = relationship("Address", backref="clients", uselist=False)

    def __init__(self, name: str, email: str, cpf: str, phone: Optional[str] = None, 
                 address_id: Optional[int] = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.cpf = cpf
        self.address_id = address_id

    @classmethod
    def create_with_address(cls, name: str, email: str, cpf: str, phone: Optional[str] = None,
                           street: Optional[str] = None, city: Optional[str] = None,
                           state: Optional[str] = None, zip_code: Optional[str] = None,
                           country: Optional[str] = None):
        """
        Método de classe para criar um cliente com endereço.
        """
        address = None
        if any([street, city, state, zip_code, country]):
            address = Address(
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
                country=country
            )
        
        client = cls(
            name=name,
            email=email,
            cpf=cpf,
            phone=phone,
            address_id=0  # Será definido após a inserção do address
        )
        
        return address, client

    def update_fields(self, name: Optional[str] = None, email: Optional[str] = None,
                     phone: Optional[str] = None, cpf: Optional[str] = None):
        """
        Atualiza os campos do cliente.
        """
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if cpf is not None:
            self.cpf = cpf

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', email='{self.email}')>"
