from sqlmodel import SQLModel
from sqlalchemy import Column, Integer, ForeignKey, Table

#Tabla de relación entre influencer y suplemento
influencer_suplemento = Table(
    "influencer_suplemento", SQLModel.metadata,
    #Llave foranea a influencer y eliminar relación con CASCADE
    Column("influencer_id", Integer, ForeignKey("influencers.id", ondelete="CASCADE"), primary_key=True),
    #Llave foranea a suplemento y eliminar relación con CASCADE
    Column("suplemento_id", Integer, ForeignKey("suplementos.id", ondelete="CASCADE"), primary_key=True),
)

#Tabla de relación entre rutina y ejercicio
rutina_ejercicio = Table(
    "rutina_ejercicio", SQLModel.metadata,
    #Llave foranea a rutina y eliminar relación con CASCADE
    Column("rutina_id", Integer, ForeignKey("rutinas.id", ondelete="CASCADE"), primary_key=True),
    #Llave foranea a ejericio y eliminar relación con CASCADE
    Column("ejercicio_id", Integer, ForeignKey("ejercicios.id", ondelete="CASCADE"), primary_key=True),
)
