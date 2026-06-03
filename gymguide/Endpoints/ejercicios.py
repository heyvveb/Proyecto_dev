from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.ejercicio import Ejercicio, EjercicioID, EjercicioUpdate
from gymguide.Operaciones.ejercicio_OP import *
from gymguide.template_utils import render

router_ejercicios = APIRouter(tags=["Ejercicios"])

# --- HTML: listado ---
@router_ejercicios.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        ejercicios = await showEjercicios(db, include_inactive=True)
        ejercicios = [r for r in ejercicios if r.status == "inactive"]
    else:
        ejercicios = await showEjercicios(db, include_inactive=False)
    return render("ejercicios.html", {
        "request": request,
        "ejercicios": ejercicios,
        "showing_inactive": showing_inactive
    })

# --- HTML: detalle ---
@router_ejercicios.get("/ejercicios/{id}", response_class=HTMLResponse)
async def ejercicio_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    ej = await showEjercicio_ID(db, id)
    if not ej:
        return HTMLResponse("Ejercicio no encontrado", status_code=404)
    rutinas = await get_ejercicio_rutinas(db, id)
    return render("ejercicio_detail.html", {
        "request": request,
        "ej": ej,
        "rutinas": rutinas
    })

# --- JSON: obtener uno ---
@router_ejercicios.get("/api/v1/ejercicios/{ejercicio_id}", response_model=EjercicioID)
async def get_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    ejercicio = await showEjercicio_ID(db, ejercicio_id)
    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return ejercicio

# --- JSON: crear ---
@router_ejercicios.post("/api/v1/ejercicios", response_model=EjercicioID, status_code=201)
async def create_ejercicio(ejercicio: Ejercicio, db: AsyncSession = Depends(get_db)):
    try:
        return await createEjercicio(db, ejercicio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- JSON: actualizar ---
@router_ejercicios.patch("/api/v1/ejercicios/{ejercicio_id}", response_model=EjercicioID)
async def update_ejercicio(ejercicio_id: int, data: EjercicioUpdate, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateEjercicio(db, ejercicio_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return updated

# --- JSON: eliminar ---
@router_ejercicios.delete("/api/v1/ejercicios/{ejercicio_id}", status_code=204)
async def delete_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteEjercicio(db, ejercicio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ejercicio not found")

# --- JSON: restaurar ---
@router_ejercicios.post("/api/v1/ejercicios/{ejercicio_id}/restore", response_model=EjercicioID)
async def restore_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreEjercicio(db, ejercicio_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Ejercicio not found or already active")
    return restored
