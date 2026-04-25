from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gymguide.Endpoints.influencers import router_influencers
from gymguide.Endpoints.rutinas import router_rutinas
from gymguide.Endpoints.suplementos import router_suplementos

app = FastAPI()

app.include_router(router_rutinas)
app.include_router(router_influencers)
app.include_router(router_suplementos)
