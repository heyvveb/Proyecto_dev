from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from gymguide.database import Base

influencer_suplemento = Table(
    "influencer_suplemento", Base.metadata,
    Column("influencer_id", Integer, ForeignKey("influencers.id", ondelete="CASCADE"), primary_key=True),
    Column("suplemento_id", Integer, ForeignKey("suplementos.id", ondelete="CASCADE"), primary_key=True),
)

rutina_ejercicio = Table(
    "rutina_ejercicio", Base.metadata,
    Column("rutina_id", Integer, ForeignKey("rutinas.id", ondelete="CASCADE"), primary_key=True),
    Column("ejercicio_id", Integer, ForeignKey("ejercicios.id", ondelete="CASCADE"), primary_key=True),
)


class InfluencerModel(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)
    logros = Column(String(500), default="")
    red_social = Column(String(200), default="")
    rutina_recomendada_id = Column(Integer, ForeignKey("rutinas.id"), nullable=True)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="active")

    rutina_recomendada = relationship("RutinaModel", back_populates="influencers", foreign_keys=[rutina_recomendada_id])
    suplementos = relationship("SuplementoModel", secondary=influencer_suplemento, back_populates="influencers")


class RutinaModel(Base):
    __tablename__ = "rutinas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False)
    objective = Column(String(100), nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="active")

    influencers = relationship("InfluencerModel", back_populates="rutina_recomendada", foreign_keys=[InfluencerModel.rutina_recomendada_id])
    ejercicios = relationship("EjercicioModel", secondary=rutina_ejercicio, back_populates="rutinas")


class SuplementoModel(Base):
    __tablename__ = "suplementos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    brand = Column(String(100), nullable=False)
    benefits = Column(String(500), default="")
    price = Column(Integer, default=0)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="active")

    influencers = relationship("InfluencerModel", secondary=influencer_suplemento, back_populates="suplementos")


class EjercicioModel(Base):
    __tablename__ = "ejercicios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    grupo_muscular = Column(String(50), nullable=False)
    descripcion = Column(String(500), default="")
    series = Column(Integer, default=3)
    repeticiones = Column(Integer, default=10)
    descanso_segundos = Column(Integer, default=60)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="active")

    rutinas = relationship("RutinaModel", secondary=rutina_ejercicio, back_populates="ejercicios")
