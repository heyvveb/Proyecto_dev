from pydantic import BaseModel, Field
from typing import Optional
from gymguide.models.enums import CategoriaEnum


class Influencer(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    categoria: CategoriaEnum
    logros: str = ""
    red_social: str = ""
    rutina_recomendada_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Chris Bumstead",
                "categoria": "bodybuilding",
                "logros": "Mr. Olympia Classic Physique 2024",
                "red_social": "@cbum",
                "rutina_recomendada_id": 1,
                "image_url": "https://example.com/cbum.jpg",
                "status": "active"
            }
        }

class InfluencerID(Influencer):
    id: int = Field(..., gt=0)
    rutina_recomendada_nombre: Optional[str] = None

class InfluencerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    categoria: Optional[CategoriaEnum] = None
    logros: Optional[str] = None
    red_social: Optional[str] = None
    rutina_recomendada_id: Optional[int] = None
    rutina_recomendada_nombre: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
