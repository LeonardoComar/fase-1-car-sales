from sqlalchemy import Column, BigInteger, String, Boolean, SMALLINT, DATETIME, ForeignKey
from app.src.infrastructure.driven.database.connection_mysql import Base
from datetime import datetime
from typing import Optional

class VehicleImage(Base):
    __tablename__ = "vehicle_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vehicle_id = Column(BigInteger, ForeignKey("motor_vehicles.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    position = Column(SMALLINT, nullable=False)
    is_primary = Column(Boolean, default=False)
    uploaded_at = Column(DATETIME, default=datetime.utcnow)

    def __init__(self, vehicle_id: int, filename: str, path: str, position: int,
                 thumbnail_path: Optional[str] = None, is_primary: bool = False):
        self.vehicle_id = vehicle_id
        self.filename = filename
        self.path = path
        self.thumbnail_path = thumbnail_path
        self.position = position
        self.is_primary = is_primary

    def __repr__(self):
        return f"<VehicleImage(id={self.id}, vehicle_id={self.vehicle_id}, position={self.position})>"
