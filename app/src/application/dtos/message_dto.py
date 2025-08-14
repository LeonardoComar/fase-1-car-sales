from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageStatus(str, Enum):
    PENDING = "Pendente"
    CONTACT_INITIATED = "Contato iniciado"
    FINISHED = "Finalizado"
    CANCELLED = "Cancelado"

# Request DTOs
class MessageCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nome do remetente")
    email: EmailStr = Field(..., description="Email do remetente")
    phone: Optional[str] = Field(None, max_length=50, description="Telefone do remetente")
    message: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    vehicle_id: Optional[int] = Field(None, description="ID do veículo relacionado")

class MessageStartServiceRequest(BaseModel):
    responsible_id: int = Field(..., description="ID do funcionário responsável")

class MessageUpdateStatusRequest(BaseModel):
    status: MessageStatus = Field(..., description="Novo status da mensagem")

# Response DTOs
class MessageResponse(BaseModel):
    id: int
    responsible_id: Optional[int]
    vehicle_id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    message: str
    status: str
    service_start_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class MessageCreatedResponse(BaseModel):
    id: int
    name: str
    email: str
    status: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
