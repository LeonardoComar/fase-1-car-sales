from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Response DTOs
class VehicleImageResponse(BaseModel):
    id: int
    vehicle_id: int
    filename: str
    path: str
    url: str  # URL completa para acessar a imagem
    thumbnail_path: Optional[str]
    thumbnail_url: Optional[str]  # URL completa para acessar o thumbnail
    position: int
    is_primary: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class VehicleImagesResponse(BaseModel):
    vehicle_id: int
    images: List[VehicleImageResponse]
    total_images: int

class ImageUploadResponse(BaseModel):
    id: int
    filename: str
    url: str
    position: int
    is_primary: bool
    message: str

# Request DTOs
class ImagePositionItem(BaseModel):
    image_id: int = Field(..., description="ID da imagem")
    position: int = Field(..., ge=1, le=10, description="Nova posição (1-10)")

class ImageReorderRequest(BaseModel):
    image_positions: List[ImagePositionItem] = Field(..., description="Lista de imagens com suas novas posições")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_positions": [
                    {"image_id": 1, "position": 3},
                    {"image_id": 2, "position": 1},
                    {"image_id": 3, "position": 2}
                ]
            }
        }

class SetPrimaryImageRequest(BaseModel):
    image_id: int = Field(..., description="ID da imagem a ser definida como principal")
