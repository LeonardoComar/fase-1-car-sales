from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from app.src.infrastructure.driven.database.connection_mysql import Base
from datetime import datetime
from typing import Optional


class MotorVehicle(Base):
    """
    Entidade base para veículos motorizados.
    Representa a tabela motor_vehicles no banco de dados.
    """
    __tablename__ = 'motor_vehicles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(100), nullable=False)
    year = Column(String(20), nullable=False)
    mileage = Column(Integer, nullable=False)
    fuel_type = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    additional_description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default='Ativo')
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __init__(self, model: str, year: str, mileage: int, fuel_type: str, 
                 color: str, city: str, price: int, additional_description: Optional[str] = None, 
                 status: str = 'Ativo', id: Optional[int] = None):
        if id is not None:
            self.id = id
        if price <= 0:
            raise ValueError("Price deve ser maior que zero")
        self.model = model
        self.year = year
        self.mileage = mileage
        self.fuel_type = fuel_type
        self.color = color
        self.city = city
        self.price = price
        self.additional_description = additional_description
        self.status = status

    def __repr__(self):
        return f"<MotorVehicle(id={self.id}, model='{self.model}', year='{self.year}')>"
