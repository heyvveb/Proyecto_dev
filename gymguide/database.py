# --- Config: cargar .env y política de eventos para Windows ---
import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# WindowsSelectorEventLoopPolicy evita error de proactor en Windows con psycopg
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Normalizar DATABASE_URL: psycopg en vez de asyncpg ---
# asyncpg falla con Neon pooler en Windows, psycopg es compatible
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/gymguide")

DATABASE_URL = DATABASE_URL.replace("&channel_binding=require", "")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# --- Engine y sesión asíncrona ---
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# --- Base declarativa para modelos ORM ---
class Base(DeclarativeBase):
    pass

# --- Dependencia: sesión por request ---
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# --- init_db: crear tablas al arrancar la app ---
async def init_db():
    async with engine.begin() as conn:
        from gymguide.models.models_sql import InfluencerModel, RutinaModel, SuplementoModel, EjercicioModel
        await conn.run_sync(Base.metadata.create_all)
