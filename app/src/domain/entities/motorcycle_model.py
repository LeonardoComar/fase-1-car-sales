from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from app.src.infrastructure.driven.database.connection_mysql import Base
from app.src.domain.entities.motor_vehicle_model import MotorVehicle
from typing import Optional


class Motorcycle(Base):
    """
    Entidade Motorcycle que herda de MotorVehicle.
    Representa a tabela motorcycles no banco de dados.
    """
    __tablename__ = 'motorcycles'

    vehicle_id = Column(Integer, ForeignKey('motor_vehicles.id', ondelete='CASCADE'), primary_key=True)
    starter = Column(String(50), nullable=False)
    fuel_system = Column(String(50), nullable=False)
    engine_displacement = Column(Integer, nullable=False)
    cooling = Column(String(50), nullable=False)
    style = Column(String(50), nullable=False)
    engine_type = Column(String(50), nullable=False)
    gears = Column(SmallInteger, nullable=False)
    front_rear_brake = Column(String(100), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacionamento com MotorVehicle
    motor_vehicle = relationship("MotorVehicle", backref="motorcycle", uselist=False)

    def __init__(self, vehicle_id: int, starter: str, fuel_system: str, engine_displacement: int,
                 cooling: str, style: str, engine_type: str, gears: int, front_rear_brake: str):
        self.vehicle_id = vehicle_id
        self.starter = starter
        self.fuel_system = fuel_system
        self.engine_displacement = engine_displacement
        self.cooling = cooling
        self.style = style
        self.engine_type = engine_type
        self.gears = gears
        self.front_rear_brake = front_rear_brake

    @classmethod
    def create_with_motor_vehicle(cls, model: str, year: str, mileage: int, fuel_type: str,
                                  color: str, city: str, price: int, starter: str, fuel_system: str,
                                  engine_displacement: int, cooling: str, style: str, engine_type: str,
                                  gears: int, front_rear_brake: str, additional_description: Optional[str] = None):
        """
        Método de classe para criar uma moto com seu veículo base.
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
            status="Ativo"  # Definindo status como "Ativo" para motos
        )
        
        motorcycle = cls(
            vehicle_id=0,  # Será definido após a inserção do motor_vehicle
            starter=starter,
            fuel_system=fuel_system,
            engine_displacement=engine_displacement,
            cooling=cooling,
            style=style,
            engine_type=engine_type,
            gears=gears,
            front_rear_brake=front_rear_brake
        )
        
        return motor_vehicle, motorcycle

    def __repr__(self):
        return f"<Motorcycle(vehicle_id={self.vehicle_id}, starter='{self.starter}', engine_displacement={self.engine_displacement})>"
