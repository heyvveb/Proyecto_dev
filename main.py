from fastapi import FastAPI
from fastapi.responses import JSONResponse
from gymguide.Endpoints.influencers import router_influencers
from gymguide.Endpoints.rutinas import router_rutinas
from gymguide.Endpoints.suplementos import router_suplementos
from gymguide.Endpoints.ejercicios import router_ejercicios
from gymguide.Endpoints.html_routes import router_html
from gymguide.database import create_all_tables



app = FastAPI(lifespan=create_all_tables)

app.include_router(router_influencers)
app.include_router(router_rutinas)
app.include_router(router_suplementos)
app.include_router(router_ejercicios)
app.include_router(router_html)
