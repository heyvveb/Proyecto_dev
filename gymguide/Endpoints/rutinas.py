from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from gymguide.database import get_db
from gymguide.models.rutina import Rutina, RutinaID, RutinaUpdate
from gymguide.Operaciones.rutina_OP import *
from gymguide.Operaciones.ejercicio_OP import showEjercicios
from gymguide.template_utils import render

class EjercicioIdsRequest(BaseModel):
    ejercicio_ids: list[int]

router_rutinas = APIRouter(tags=["Rutinas"])

# --- HTML: listado ---
@router_rutinas.get("/rutinas", response_class=HTMLResponse)
async def rutinas_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        rutinas = await showRutinas(db, include_inactive=True)
        rutinas = [r for r in rutinas if r.status == "inactive"]
    else:
        rutinas = await showRutinas(db, include_inactive=False)
    all_ejercicios = await showEjercicios(db)
    return render("rutinas.html", {
        "request": request,
        "rutinas": rutinas,
        "all_ejercicios": all_ejercicios,
        "showing_inactive": showing_inactive
    })

# --- HTML: detalle ---
@router_rutinas.get("/rutinas/{id}", response_class=HTMLResponse)
async def rutina_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    rut = await showRutina_ID(db, id)
    if not rut:
        return HTMLResponse("Rutina no encontrada", status_code=404)
    ejercicios = await get_rutina_ejercicios(db, id)
    influencers = await get_rutina_influencers(db, id)
    return render("rutina_detail.html", {
        "request": request,
        "rut": rut,
        "ejercicios": ejercicios,
        "influencers": influencers
    })

# --- JSON: obtener uno ---
@router_rutinas.get("/api/v1/rutinas/{rutina_id}", response_model=RutinaID)
async def get_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    rutina = await showRutina_ID(db, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return rutina

# --- JSON: crear ---
@router_rutinas.post("/api/v1/rutinas", response_model=RutinaID, status_code=201)
async def create_rutina(rutina: Rutina, db: AsyncSession = Depends(get_db)):
    try:
        return await createRutina(db, rutina)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- JSON: actualizar ---
@router_rutinas.patch("/api/v1/rutinas/{rutina_id}", response_model=RutinaID)
async def update_rutina(rutina_id: int, data: RutinaUpdate, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateRutina(db, rutina_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return updated

# --- JSON: eliminar ---
@router_rutinas.delete("/api/v1/rutinas/{rutina_id}", status_code=204)
async def delete_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteRutina(db, rutina_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rutina not found")

# --- JSON: asignar ejercicios M:N ---
@router_rutinas.put("/api/v1/rutinas/{rutina_id}/ejercicios", response_model=RutinaID)
async def set_rutina_ejercicios_endpoint(rutina_id: int, body: EjercicioIdsRequest, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    result = await set_rutina_ejercicios(db, rutina_id, body.ejercicio_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return result

# --- JSON: restaurar ---
@router_rutinas.post("/api/v1/rutinas/{rutina_id}/restore", response_model=RutinaID)
async def restore_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreRutina(db, rutina_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Rutina not found or already active")
    return restored
