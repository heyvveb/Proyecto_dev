from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from gymguide.database import get_db
from gymguide.models.rutina import Rutina, RutinaRead, RutinaUpdate
from gymguide.Operaciones.rutina_OP import *
from gymguide.Operaciones.ejercicio_OP import showEjercicios
from gymguide.template_utils import render

class EjercicioIdsRequest(BaseModel):
    ejercicio_ids: list[int]

router_rutinas = APIRouter(tags=["Rutinas"])

#  listado 
@router_rutinas.get("/rutinas", response_class=HTMLResponse)
async def rutinas_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    # Verifica si se muestran inactivos
    showing_inactive = status == "inactive"
    if showing_inactive:
        rutinas = await showRutinas(db, include_inactive=True)
        rutinas = [r for r in rutinas if r.status == "inactive"]
    else:
        rutinas = await showRutinas(db, include_inactive=False)
    # Obtiene todos los ejercicios
    all_ejercicios = await showEjercicios(db)
    # Renderiza la vista
    return render("rutinas.html", {
        "request": request,
        "rutinas": rutinas,
        "all_ejercicios": all_ejercicios,
        "showing_inactive": showing_inactive
    })

# Vista en detalle 
@router_rutinas.get("/rutinas/{id}", response_class=HTMLResponse)
async def rutina_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    # Busca la rutina por ID
    rut = await showRutina_ID(db, id)
    # Retorna error si no existe
    if not rut:
        return HTMLResponse("Rutina no encontrada", status_code=404)
    # Obtiene ejercicios e influencers asociados
    ejercicios = await get_rutina_ejercicios(db, id)
    influencers = await get_rutina_influencers(db, id)
    # Renderiza la vista
    return render("rutina_detail.html", {
        "request": request,
        "rut": rut,
        "ejercicios": ejercicios,
        "influencers": influencers
    })

# obtener uno 
@router_rutinas.get("/api/v1/rutinas/{rutina_id}", response_model=RutinaRead)
async def get_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Busca la rutina
    rutina = await showRutina_ID(db, rutina_id)
    # Retorna error si no existe
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return rutina

# crear 
@router_rutinas.post("/api/v1/rutinas", response_model=RutinaRead, status_code=201)
async def create_rutina(rutina: Rutina, db: AsyncSession = Depends(get_db)):
    try:
        # Crea la rutina
        return await createRutina(db, rutina)
    # Maneja errores de validación
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# actualizar 
@router_rutinas.patch("/api/v1/rutinas/{rutina_id}", response_model=RutinaRead)
async def update_rutina(rutina_id: int, data: RutinaUpdate, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Actualiza la rutina
    updated = await updateRutina(db, rutina_id, data.model_dump(exclude_unset=True))
    # Retorna error si no existe
    if not updated:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return updated

# eliminar 
@router_rutinas.delete("/api/v1/rutinas/{rutina_id}", status_code=204)
async def delete_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Elimina la rutina
    deleted = await deleteRutina(db, rutina_id)
    # Retorna error si no existe
    if not deleted:
        raise HTTPException(status_code=404, detail="Rutina not found")

# asignar ejercicios 
@router_rutinas.put("/api/v1/rutinas/{rutina_id}/ejercicios", response_model=RutinaRead)
async def set_rutina_ejercicios_endpoint(rutina_id: int, body: EjercicioIdsRequest, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Asigna ejercicios a la rutina
    result = await set_rutina_ejercicios(db, rutina_id, body.ejercicio_ids)
    # Retorna error si no existe
    if not result:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return result

# restaurar 
@router_rutinas.post("/api/v1/rutinas/{rutina_id}/restore", response_model=RutinaRead)
async def restore_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Restaura la rutina
    restored = await restoreRutina(db, rutina_id)
    # Retorna error si no existe o ya está activa
    if not restored:
        raise HTTPException(status_code=404, detail="Rutina not found or already active")
    return restored
