from pydantic import BaseModel, Field
from typing import Optional
from gymguide.models.enums import LevelEnum, ObjectiveEnum


class Rutina(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: LevelEnum
    objective: ObjectiveEnum
    duration_weeks: int = Field(..., ge=1, le=52)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Programa de Hipertrofia",
                "level": "Intermedio",
                "objective": "Ganancia Muscular",
                "duration_weeks": 12,
                "image_url": "https://example.com/rutina.jpg",
                "status": "active"
            }
        }

class RutinaID(Rutina):
    id: int = Field(..., gt=0)

class RutinaUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    level: Optional[LevelEnum] = None
    objective: Optional[ObjectiveEnum] = None
    duration_weeks: Optional[int] = Field(None, ge=1, le=52)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
