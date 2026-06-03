from sqlmodel import SQLModel
from sqlalchemy import Column, Integer, ForeignKey, Table

influencer_suplemento = Table(
    "influencer_suplemento", SQLModel.metadata,
    Column("influencer_id", Integer, ForeignKey("influencers.id", ondelete="CASCADE"), primary_key=True),
    Column("suplemento_id", Integer, ForeignKey("suplementos.id", ondelete="CASCADE"), primary_key=True),
)

rutina_ejercicio = Table(
    "rutina_ejercicio", SQLModel.metadata,
    Column("rutina_id", Integer, ForeignKey("rutinas.id", ondelete="CASCADE"), primary_key=True),
    Column("ejercicio_id", Integer, ForeignKey("ejercicios.id", ondelete="CASCADE"), primary_key=True),
)
