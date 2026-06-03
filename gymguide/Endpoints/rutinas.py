from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from gymguide.database import SessionDep
from gymguide.models.rutina import Rutina, RutinaRead, RutinaUpdate
from gymguide.Operaciones.rutina_OP import *
from gymguide.Operaciones.ejercicio_OP import showEjercicios
from gymguide.template_utils import render

class EjercicioIdsRequest(BaseModel):
    ejercicio_ids: list[int]

router_rutinas = APIRouter(tags=["Rutinas"])

#  listado 
@router_rutinas.get("/rutinas", response_class=HTMLResponse)
def rutinas_page(request: Request, db: SessionDep, status: str = "active"):
    # Verifica si se muestran inactivos
    showing_inactive = status == "inactive"
    if showing_inactive:
        rutinas = showRutinas(db, include_inactive=True)
        rutinas = [r for r in rutinas if r.status == "inactive"]
    else:
        rutinas = showRutinas(db, include_inactive=False)
    # Obtiene todos los ejercicios
    all_ejercicios = showEjercicios(db)
    # Renderiza la vista
    return render("rutinas.html", {
        "request": request,
        "rutinas": rutinas,
        "all_ejercicios": all_ejercicios,
        "showing_inactive": showing_inactive
    })

# Vista en detalle 
@router_rutinas.get("/rutinas/{id}", response_class=HTMLResponse)
def rutina_detail(request: Request, id: int, db: SessionDep):
    # Busca la rutina por ID
    rut = showRutina_ID(db, id)
    # Retorna error si no existe
    if not rut:
        return HTMLResponse("Rutina no encontrada", status_code=404)
    # Obtiene ejercicios e influencers asociados
    ejercicios = get_rutina_ejercicios(db, id)
    influencers = get_rutina_influencers(db, id)
    # Renderiza la vista
    return render("rutina_detail.html", {
        "request": request,
        "rut": rut,
        "ejercicios": ejercicios,
        "influencers": influencers
    })

# obtener uno 
@router_rutinas.get("/api/v1/rutinas/{rutina_id}", response_model=RutinaRead)
def get_rutina(rutina_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Busca la rutina
    rutina = showRutina_ID(db, rutina_id)
    # Retorna error si no existe
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return rutina

# crear 
@router_rutinas.post("/api/v1/rutinas", response_model=RutinaRead, status_code=201)
def create_rutina(rutina: Rutina, db: SessionDep):
    try:
        return createRutina(db, rutina)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# actualizar 
@router_rutinas.patch("/api/v1/rutinas/{rutina_id}", response_model=RutinaRead)
def update_rutina(rutina_id: int, data: RutinaUpdate, db: SessionDep):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Actualiza la rutina
    updated = updateRutina(db, rutina_id, data.model_dump(exclude_unset=True))
    # Retorna error si no existe
    if not updated:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return updated

# eliminar 
@router_rutinas.delete("/api/v1/rutinas/{rutina_id}", status_code=204)
def delete_rutina(rutina_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Elimina la rutina
    deleted = deleteRutina(db, rutina_id)
    # Retorna error si no existe
    if not deleted:
        raise HTTPException(status_code=404, detail="Rutina not found")

# asignar ejercicios 
@router_rutinas.put("/api/v1/rutinas/{rutina_id}/ejercicios", response_model=RutinaRead)
def set_rutina_ejercicios_endpoint(rutina_id: int, body: EjercicioIdsRequest, db: SessionDep):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Asigna ejercicios a la rutina
    result = set_rutina_ejercicios(db, rutina_id, body.ejercicio_ids)
    # Retorna error si no existe
    if not result:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return result

# restaurar 
@router_rutinas.post("/api/v1/rutinas/{rutina_id}/restore", response_model=RutinaRead)
def restore_rutina(rutina_id: int, db: SessionDep):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Restaura la rutina
    restored = restoreRutina(db, rutina_id)
    # Retorna error si no existe o ya está activa
    if not restored:
        raise HTTPException(status_code=404, detail="Rutina not found or already active")
    return restored
