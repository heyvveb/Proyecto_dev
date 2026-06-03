from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from gymguide.models.enums import CategoriaEnum
from gymguide.models.associations import influencer_suplemento

#Influencer base
class Influencer(SQLModel, table=True):
    __tablename__ = "influencers"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    categoria: CategoriaEnum
    logros: str = ""
    red_social: str = ""
    rutina_recomendada_id: Optional[int] = Field(default=None, foreign_key="rutinas.id", ondelete="SET NULL")
    image_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="active")
    #Rutina recomendada por el influencer
    rutina_recomendada: Optional["Rutina"] = Relationship(back_populates="influencers")
    #Lista de suplementos que tiene es influencer
    suplementos: list["Suplemento"] = Relationship(back_populates="influencers", sa_relationship_kwargs={"secondary": influencer_suplemento})

#Actualizar un influencer
class InfluencerUpdate(SQLModel, table=False):
    name: Optional[str] = Field(None, max_length=100)
    categoria: Optional[CategoriaEnum] = None
    logros: Optional[str] = None
    red_social: Optional[str] = None
    rutina_recomendada_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None)
    rutina_recomendada_nombre: Optional[str] = None
    suplemento_ids: Optional[list[int]] = None

#Obtener un influencer
class InfluencerRead(SQLModel, table=False):
    id: int
    name: str
    categoria: CategoriaEnum
    logros: str
    red_social: str
    rutina_recomendada_id: Optional[int] = None
    rutina_recomendada_nombre: Optional[str] = None
    suplemento_ids: list[int] = []
    image_url: str
    status: str
