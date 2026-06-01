from pydantic import BaseModel, Field
from typing import Optional
from gymguide.models.enums import GrupoMuscularEnum


class Ejercicio(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    grupo_muscular: GrupoMuscularEnum
    descripcion: str = ""
    series: int = Field(default=3, ge=1, le=20)
    repeticiones: int = Field(default=10, ge=1, le=100)
    descanso_segundos: int = Field(default=60, ge=0, le=600)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(default="active", pattern="^(active|inactive)$")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Press de Banca",
                "grupo_muscular": "Pecho",
                "descripcion": "Ejercicio compuesto para pectorales, hombros y tríceps.",
                "series": 4,
                "repeticiones": 10,
                "descanso_segundos": 90,
                "image_url": "https://example.com/benchpress.jpg",
                "status": "active"
            }
        }

class EjercicioID(Ejercicio):
    id: int = Field(..., gt=0)

class EjercicioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    grupo_muscular: Optional[GrupoMuscularEnum] = None
    descripcion: Optional[str] = None
    series: Optional[int] = Field(None, ge=1, le=20)
    repeticiones: Optional[int] = Field(None, ge=1, le=100)
    descanso_segundos: Optional[int] = Field(None, ge=0, le=600)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
