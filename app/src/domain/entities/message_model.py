from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, ForeignKey
from app.src.infrastructure.driven.database.connection_mysql import Base
from datetime import datetime
from enum import Enum

class MessageStatus(str, Enum):
    PENDING = "Pendente"
    CONTACT_INITIATED = "Contato iniciado"
    FINISHED = "Finalizado"
    CANCELLED = "Cancelado"

class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    responsible_id = Column(BigInteger, ForeignKey("employees.id"), nullable=True)
    vehicle_id = Column(BigInteger, ForeignKey("motor_vehicles.id"), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default=MessageStatus.PENDING.value)
    service_start_time = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Message(id={self.id}, name='{self.name}', status='{self.status}')>"
