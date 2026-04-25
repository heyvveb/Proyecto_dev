from pydantic import BaseModel, Field
from typing import Optional


class Suplemento(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(Proteina|Creatina|Pre-Entreno|Amino acidos|Vitaminas|Fat burner)$")
    brand: str
    benefits: str
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Whey Protein Isolate",
                "type": "Proteina",
                "brand": "Optimum Nutrition",
                "benefits": "Proteina de rápida absorción para la recuperación muscular.",
                "status": "active"
            }
        }

class SuplementoID(Suplemento):
    id: int = Field(...,gt=0)

class SuplementoUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(Proteina|Creatina|Pre-Entreno|Amino acidos|Vitaminas|Fat burner)$")
    brand: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")