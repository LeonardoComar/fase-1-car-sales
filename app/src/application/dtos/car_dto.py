from pydantic import BaseModel, Field
from typing import Optional


class CreateCarRequest(BaseModel):
    """
    DTO para requisição de criação de carro.
    """
    # Dados do veículo base (MotorVehicle)
    model: str = Field(..., min_length=1, max_length=100, description="Modelo do veículo")
    year: str = Field(..., min_length=4, max_length=20, description="Ano do veículo")
    mileage: int = Field(..., ge=0, description="Quilometragem do veículo")
    fuel_type: str = Field(..., min_length=1, max_length=20, description="Tipo de combustível")
    color: str = Field(..., min_length=1, max_length=50, description="Cor do veículo")
    city: str = Field(..., min_length=1, max_length=100, description="Cidade onde está o veículo")
    price: int = Field(..., gt=0, description="Preço do veículo (deve ser maior que zero)")
    additional_description: Optional[str] = Field(None, description="Descrição adicional do veículo")
    
    # Dados específicos do carro
    bodywork: str = Field(..., min_length=1, max_length=20, description="Tipo de carroceria")
    transmission: str = Field(..., min_length=1, max_length=20, description="Tipo de transmissão")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "Honda Civic",
                "year": "2020",
                "mileage": 25000,
                "fuel_type": "Flex",
                "color": "Branco",
                "city": "São Paulo",
                "price": 85000,
                "additional_description": "Carro em excelente estado de conservação",
                "bodywork": "Sedan",
                "transmission": "Automático"
            }
        }


class CarResponse(BaseModel):
    """
    DTO para resposta da criação/consulta de carro.
    """
    id: int
    model: str
    year: str
    mileage: int
    fuel_type: str
    color: str
    city: str
    price: int
    additional_description: Optional[str]
    status: str
    bodywork: str
    transmission: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "model": "Honda Civic",
                "year": "2020",
                "mileage": 25000,
                "fuel_type": "Flex",
                "color": "Branco",
                "city": "São Paulo",
                "price": 85000,
                "additional_description": "Carro em excelente estado de conservação",
                "status": "Ativo",
                "bodywork": "Sedan",
                "transmission": "Automático",
                "created_at": "2025-08-07T10:30:00",
                "updated_at": "2025-08-07T10:30:00"
            }
        }
