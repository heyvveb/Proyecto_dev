import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from gymguide.Endpoints.influencers import router_influencers
from gymguide.Endpoints.rutinas import router_rutinas
from gymguide.Endpoints.suplementos import router_suplementos
from gymguide.Endpoints.ejercicios import router_ejercicios
from gymguide.Endpoints.html_routes import router_html
from gymguide.database import init_db, async_session
from gymguide.models.models_sql import InfluencerModel, RutinaModel, SuplementoModel, EjercicioModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router_rutinas)
app.include_router(router_influencers)
app.include_router(router_suplementos)
app.include_router(router_ejercicios)
app.include_router(router_html)
