from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class CreateClientRequest(BaseModel):
    """
    DTO para requisição de criação de cliente.
    """
    # Dados do cliente
    name: str = Field(..., min_length=1, max_length=100, description="Nome do cliente")
    email: EmailStr = Field(..., description="Email do cliente")
    phone: Optional[str] = Field(None, max_length=50, description="Telefone do cliente")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do cliente")
    
    # Dados do endereço (opcional)
    street: Optional[str] = Field(None, max_length=100, description="Rua do endereço")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do endereço")
    state: Optional[str] = Field(None, max_length=100, description="Estado do endereço")
    zip_code: Optional[str] = Field(None, max_length=20, description="CEP do endereço")
    country: Optional[str] = Field(None, max_length=100, description="País do endereço")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "email": "joao.silva@email.com",
                "phone": "(11) 99999-9999",
                "cpf": "123.456.789-00",
                "street": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234-567",
                "country": "Brasil"
            }
        }


class UpdateClientRequest(BaseModel):
    """
    DTO para requisição de atualização de cliente.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do cliente")
    email: Optional[EmailStr] = Field(None, description="Email do cliente")
    phone: Optional[str] = Field(None, max_length=50, description="Telefone do cliente")
    cpf: Optional[str] = Field(None, min_length=11, max_length=14, description="CPF do cliente")
    
    # Dados do endereço (opcional)
    street: Optional[str] = Field(None, max_length=100, description="Rua do endereço")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do endereço")
    state: Optional[str] = Field(None, max_length=100, description="Estado do endereço")
    zip_code: Optional[str] = Field(None, max_length=20, description="CEP do endereço")
    country: Optional[str] = Field(None, max_length=100, description="País do endereço")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "email": "joao.silva@email.com",
                "phone": "(11) 99999-9999",
                "cpf": "123.456.789-00",
                "street": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234-567",
                "country": "Brasil"
            }
        }


class AddressResponse(BaseModel):
    """
    DTO para resposta do endereço.
    """
    id: int
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]

    class Config:
        from_attributes = True


class ClientResponse(BaseModel):
    """
    DTO para resposta da criação/consulta de cliente.
    """
    id: int
    name: str
    email: str
    phone: Optional[str]
    cpf: str
    address: Optional[AddressResponse]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "João Silva",
                "email": "joao.silva@email.com",
                "phone": "(11) 99999-9999",
                "cpf": "123.456.789-00",
                "address": {
                    "id": 1,
                    "street": "Rua das Flores, 123",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "Brasil"
                },
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            }
        }


class ClientListResponse(BaseModel):
    """
    DTO para resposta da listagem de clientes.
    """
    id: int
    name: str
    email: str
    phone: Optional[str]
    cpf: str
    city: Optional[str]  # Cidade do endereço para facilitar a listagem

    class Config:
        from_attributes = True
