from fastapi import FastAPI
from gymguide.Endpoints.influencers import router_influencers
from gymguide.Endpoints.rutinas import router_rutinas
from gymguide.Endpoints.suplementos import router_suplementos

app = FastAPI()

app.include_router(router_influencers)
app.include_router(router_rutinas)
app.include_router(router_suplementos)


@app.get("/")
def root():
    return {"message": "Welcome to GymGuide API"}


@app.get("/health")
def health():
    return {"status": "healthy"}