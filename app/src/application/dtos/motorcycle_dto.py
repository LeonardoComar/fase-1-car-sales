from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal

# Import compartilhado
class VehicleImageInfo(BaseModel):
    """
    DTO para informações básicas de imagem do veículo
    """
    id: int
    url: str
    thumbnail_url: Optional[str]
    position: int
    is_primary: bool


class CreateMotorcycleRequest(BaseModel):
    """
    DTO para requisição de criação de moto.
    """
    # Dados do veículo base (MotorVehicle)
    model: str = Field(..., min_length=1, max_length=100, description="Modelo do veículo")
    year: str = Field(..., min_length=4, max_length=20, description="Ano do veículo")
    mileage: int = Field(..., ge=0, description="Quilometragem do veículo")
    fuel_type: str = Field(..., min_length=1, max_length=20, description="Tipo de combustível")
    color: str = Field(..., min_length=1, max_length=50, description="Cor do veículo")
    city: str = Field(..., min_length=1, max_length=100, description="Cidade onde está o veículo")
    price: Decimal = Field(..., gt=0, description="Preço do veículo (deve ser maior que zero)")
    additional_description: Optional[str] = Field(None, description="Descrição adicional do veículo")
    
    # Dados específicos da moto
    starter: str = Field(..., min_length=1, max_length=50, description="Tipo de partida")
    fuel_system: str = Field(..., min_length=1, max_length=50, description="Sistema de combustível")
    engine_displacement: int = Field(..., gt=0, description="Cilindrada do motor (deve ser maior que zero)")
    cooling: str = Field(..., min_length=1, max_length=50, description="Sistema de arrefecimento")
    style: str = Field(..., min_length=1, max_length=50, description="Estilo da moto")
    engine_type: str = Field(..., min_length=1, max_length=50, description="Tipo do motor")
    gears: int = Field(..., gt=0, description="Número de marchas (deve ser maior que zero)")
    front_rear_brake: str = Field(..., min_length=1, max_length=100, description="Sistema de freios dianteiro/traseiro")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "Honda CB 600F Hornet",
                "year": "2021",
                "mileage": 15000,
                "fuel_type": "Gasolina",
                "color": "Azul",
                "city": "São Paulo",
                "price": "32000.00",
                "additional_description": "Moto em excelente estado de conservação",
                "starter": "Elétrico",
                "fuel_system": "Injeção eletrônica",
                "engine_displacement": 600,
                "cooling": "Líquido",
                "style": "Naked",
                "engine_type": "4 cilindros",
                "gears": 6,
                "front_rear_brake": "Disco/Disco"
            }
        }


class MotorcycleResponse(BaseModel):
    """
    DTO para resposta da criação/consulta de moto.
    """
    id: int
    model: str
    year: str
    mileage: int
    fuel_type: str
    color: str
    city: str
    price: Decimal
    additional_description: Optional[str]
    status: str
    starter: str
    fuel_system: str
    engine_displacement: int
    cooling: str
    style: str
    engine_type: str
    gears: int
    front_rear_brake: str
    created_at: str
    updated_at: str
    images: List[VehicleImageInfo] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "model": "Honda CB 600F Hornet",
                "year": "2021",
                "mileage": 15000,
                "fuel_type": "Gasolina",
                "color": "Azul",
                "city": "São Paulo",
                "price": "32000.00",
                "additional_description": "Moto em excelente estado de conservação",
                "status": "Ativo",
                "starter": "Elétrico",
                "fuel_system": "Injeção eletrônica",
                "engine_displacement": 600,
                "cooling": "Líquido",
                "style": "Naked",
                "engine_type": "4 cilindros",
                "gears": 6,
                "front_rear_brake": "Disco/Disco",
                "created_at": "2025-08-10T10:30:00",
                "updated_at": "2025-08-10T10:30:00",
                "images": [
                    {
                        "id": 1,
                        "url": "/static/uploads/motorcycles/1/image1.jpg",
                        "thumbnail_url": "/static/uploads/thumbnails/motorcycles/1/thumb_image1.jpg",
                        "position": 1,
                        "is_primary": True
                    }
                ]
            }
        }


class MotorcyclesListResponse(BaseModel):
    """
    DTO para resposta de lista de motocicletas com metadados.
    """
    motorcycles: List[MotorcycleResponse]
    total: int
    skip: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "motorcycles": [
                    {
                        "id": 1,
                        "model": "Honda CB 600F Hornet",
                        "year": "2021",
                        "mileage": 15000,
                        "fuel_type": "Gasolina",
                        "color": "Azul",
                        "city": "São Paulo",
                        "price": "32000.00",
                        "additional_description": "Moto em excelente estado",
                        "status": "Ativo",
                        "starter": "Elétrico",
                        "fuel_system": "Injeção eletrônica",
                        "engine_displacement": 600,
                        "cooling": "Líquido",
                        "style": "Naked",
                        "engine_type": "4 cilindros",
                        "gears": 6,
                        "front_rear_brake": "Disco/Disco",
                        "created_at": "2025-08-10T10:30:00",
                        "updated_at": "2025-08-10T10:30:00"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }
