from pydantic import BaseModel, Field
from typing import Optional
from gymguide.models.enums import TipoSuplementoEnum


class Suplemento(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: TipoSuplementoEnum
    brand: str = Field(..., max_length=100)
    benefits: str = ""
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Whey Protein Isolate",
                "type": "Proteina",
                "brand": "Optimum Nutrition",
                "benefits": "Proteina de rápida absorción para la recuperación muscular.",
                "price": 49.99,
                "image_url": "https://example.com/whey.jpg",
                "status": "active"
            }
        }

class SuplementoID(Suplemento):
    id: int = Field(..., gt=0)

class SuplementoUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[TipoSuplementoEnum] = None
    brand: Optional[str] = None
    benefits: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
