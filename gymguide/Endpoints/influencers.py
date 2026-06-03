from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from gymguide.database import SessionDep
from gymguide.models.influencer import Influencer, InfluencerRead, InfluencerUpdate
from gymguide.Operaciones.influencers_op import *
from gymguide.Operaciones.suplemento_OP import showSuplementos
from gymguide.template_utils import render

class SuplementoIdsRequest(BaseModel):
    suplemento_ids: list[int]

router_influencers = APIRouter(tags=["Influencers"])

# Mostrar influencers
@router_influencers.get("/influencers", response_class=HTMLResponse)
def influencers_page(request: Request, db: SessionDep, status: str = "active"):
    # Verifica si se deben mostrar inactivos
    showing_inactive = status == "inactive"
    if showing_inactive:
        influencers = showInfluencers(db, include_inactive=True)
        influencers = [r for r in influencers if r.status == "inactive"]
    else:
        influencers = showInfluencers(db, include_inactive=False)
    # Obtiene todos los suplementos
    all_suplementos = showSuplementos(db)
    # Obtiene nombres únicos de rutinas recomendadas
    rutinas_nombres = sorted(set(
        inf.rutina_recomendada_nombre for inf in influencers
        if inf.rutina_recomendada_nombre
    ))
    # Renderiza la vista
    return render("influencers.html", {
        "request": request,
        "influencers": influencers,
        "all_suplementos": all_suplementos,
        "rutinas_nombres": rutinas_nombres,
        "showing_inactive": showing_inactive
    })

# Vista en detalle de influencer
@router_influencers.get("/influencers/{id}", response_class=HTMLResponse)
def influencer_detail(request: Request, id: int, db: SessionDep):
    # Busca el influencer por ID
    inf = showInfluencer_ID(db, id)
    # Retorna error si no existe
    if not inf:
        return HTMLResponse("Influencer no encontrado", status_code=404)
    # Obtiene suplementos asociados
    suplementos = get_influencer_suplementos(db, id)
    # Renderiza la vista
    return render("influencer_detail.html", {
        "request": request,
        "inf": inf,
        "suplementos": suplementos
    })

# obtener uno 
@router_influencers.get("/api/v1/influencers/{influencer_id}", response_model=InfluencerRead)
def get_influencer(influencer_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Busca el influence
    influencer = showInfluencer_ID(db, influencer_id)
    # Retorna error si no existe
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return influencer

# crear 
@router_influencers.post("/api/v1/influencers", response_model=InfluencerRead, status_code=201)
def create_influencer(influencer: Influencer, db: SessionDep):
    try:
        return createInfluencer(db, influencer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_influencers.patch("/api/v1/influencers/{influencer_id}", response_model=InfluencerRead)
def update_influencer(influencer_id: int, data: InfluencerUpdate, db: SessionDep):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    try:
        updated = updateInfluencer(db, influencer_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Retorna error si no existe
    if not updated:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return updated

# eliminar 
@router_influencers.delete("/api/v1/influencers/{influencer_id}", status_code=204)
def delete_influencer(influencer_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Elimina el influencer
    deleted = deleteInfluencer(db, influencer_id)
    # Retorna error si no existe
    if not deleted:
        raise HTTPException(status_code=404, detail="Influencer not found")

# asignar suplementos 
@router_influencers.put("/api/v1/influencers/{influencer_id}/suplementos", response_model=InfluencerRead)
def set_influencer_suplementos_endpoint(influencer_id: int, body: SuplementoIdsRequest, db: SessionDep):
    # Valida que el ID sea positivo
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Asigna los suplementos al influencer
    result = set_influencer_suplementos(db, influencer_id, body.suplemento_ids)
    # Retorna error si no existe
    if not result:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return result

# restaurar 
@router_influencers.post("/api/v1/influencers/{influencer_id}/restore", response_model=InfluencerRead)
def restore_influencer(influencer_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Restaura el influencer
    restored = restoreInfluencer(db, influencer_id)
    # Retorna error si no existe o ya está activo
    if not restored:
        raise HTTPException(status_code=404, detail="Influencer not found or already active")
    return restored
