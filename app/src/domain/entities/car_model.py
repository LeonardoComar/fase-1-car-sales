from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from typing import Optional


class Car(Base):
    """
    Entidade Car que herda de MotorVehicle.
    Representa a tabela cars no banco de dados.
    """
    __tablename__ = 'cars'

    vehicle_id = Column(Integer, ForeignKey('motor_vehicles.id', ondelete='CASCADE'), primary_key=True)
    bodywork = Column(String(20), nullable=False)
    transmission = Column(String(20), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamento com MotorVehicle
    motor_vehicle = relationship("MotorVehicle", backref="car", uselist=False)

    def __init__(self, vehicle_id: int, bodywork: str, transmission: str):
        self.vehicle_id = vehicle_id
        self.bodywork = bodywork
        self.transmission = transmission

    @classmethod
    def create_with_motor_vehicle(cls, model: str, year: str, mileage: int, fuel_type: str,
                                  color: str, city: str, price: int, bodywork: str, transmission: str,
                                  additional_description: Optional[str] = None):
        """
        Método de classe para criar um carro com seu veículo base.
        """
        motor_vehicle = MotorVehicle(
            model=model,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            color=color,
            city=city,
            price=price,
            additional_description=additional_description,
            status="Ativo"  # Definindo status como "Ativo" para carros
        )
        
        car = cls(
            vehicle_id=0,  # Será definido após a inserção do motor_vehicle
            bodywork=bodywork,
            transmission=transmission
        )
        
        return motor_vehicle, car

    def __repr__(self):
        return f"<Car(vehicle_id={self.vehicle_id}, bodywork='{self.bodywork}', transmission='{self.transmission}')>"
