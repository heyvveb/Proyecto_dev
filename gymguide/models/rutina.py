from pydantic import BaseModel, Field
from typing import Optional


class Rutina(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., pattern="^(Principiante|Intermedio|Avanzado)$")
    objective: str = Field(..., pattern="^(Ganancia Muscular|Perdida de grasa|Fuerza|Resitencia)$")
    duration_weeks: int = Field(..., ge=1, le=52)
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Programa de Hipertrofia",
                "level": "Intermedio",
                "objective": "Ganancia Muscular",
                "duration_weeks": 12,
                "status": "active"
            }
        }
class RutinaID(Rutina):
    id: int = Field(...,gt=0)

class RutinaUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    level: Optional[str] = Field(None, pattern="^(Principiante|Intermedio|Avanzado)$")
    objective: Optional[str] = Field(None, pattern="^(Ganancia Muscular|Perdida de grasa|Fuerza|Resitencia)$")
    duration_weeks: Optional[int] = Field(None, ge=1, le=52)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")