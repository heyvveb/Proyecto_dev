from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Column
from typing import Optional
from gymguide.models.enums import LevelEnum, ObjectiveEnum
from gymguide.models.associations import rutina_ejercicio

#Rutina base
class Rutina(SQLModel, table=True):
    __tablename__ = "rutinas"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    level: LevelEnum
    objective: ObjectiveEnum = Field(sa_column=Column(SAEnum(ObjectiveEnum, values_callable=lambda x: [e.value for e in x])))
    duration_weeks: int
    image_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="active")
    #Influencer con esta rutina
    influencers: list["Influencer"] = Relationship(back_populates="rutina_recomendada")
    #Lsita de ejercicios que tiene esta rutina
    ejercicios: list["Ejercicio"] = Relationship(back_populates="rutinas", sa_relationship_kwargs={"secondary": rutina_ejercicio})

#Obtener una rutina
class RutinaUpdate(SQLModel, table=False):
    name: Optional[str] = Field(None, max_length=100)
    level: Optional[LevelEnum] = None
    objective: Optional[ObjectiveEnum] = None
    duration_weeks: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None)
    ejercicio_ids: Optional[list[int]] = None


class RutinaRead(SQLModel, table=False):
    id: int
    name: str
    level: LevelEnum
    objective: ObjectiveEnum
    duration_weeks: int
    ejercicio_ids: list[int] = []
    image_url: str
    status: str
