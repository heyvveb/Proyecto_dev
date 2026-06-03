from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from typing import Optional
from gymguide.models.enums import TipoSuplementoEnum
from gymguide.models.associations import influencer_suplemento

#Suplemento base
class Suplemento(SQLModel, table=True):
    __tablename__ = "suplementos"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    type: TipoSuplementoEnum = Field(sa_column=Column("type", String(50), nullable=False))
    brand: str = Field(max_length=100)
    benefits: str = ""
    price: float = Field(default=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="active")
    #Lista de influencers con este suplemento
    influencers: list["Influencer"] = Relationship(back_populates="suplementos", sa_relationship_kwargs={"secondary": influencer_suplemento})

#Actualizar suplemento
class SuplementoUpdate(SQLModel, table=False):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[TipoSuplementoEnum] = None
    brand: Optional[str] = None
    benefits: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None)

#Obtener suplemento
class SuplementoRead(SQLModel, table=False):
    id: int
    name: str
    type: str
    brand: str
    benefits: str
    price: float
    image_url: str
    status: str
