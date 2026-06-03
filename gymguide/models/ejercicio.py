from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from gymguide.models.enums import GrupoMuscularEnum
from gymguide.models.associations import rutina_ejercicio


class Ejercicio(SQLModel, table=True):
    __tablename__ = "ejercicios"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    grupo_muscular: GrupoMuscularEnum
    descripcion: str = ""
    series: int = Field(default=3)
    repeticiones: int = Field(default=10)
    descanso_segundos: int = Field(default=60)
    image_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="active")

    rutinas: list["Rutina"] = Relationship(back_populates="ejercicios", sa_relationship_kwargs={"secondary": rutina_ejercicio})


class EjercicioUpdate(SQLModel, table=False):
    name: Optional[str] = Field(None, max_length=100)
    grupo_muscular: Optional[GrupoMuscularEnum] = None
    descripcion: Optional[str] = None
    series: Optional[int] = None
    repeticiones: Optional[int] = None
    descanso_segundos: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None)


class EjercicioRead(SQLModel, table=False):
    id: int
    name: str
    grupo_muscular: GrupoMuscularEnum
    descripcion: str
    series: int
    repeticiones: int
    descanso_segundos: int
    image_url: str
    status: str
