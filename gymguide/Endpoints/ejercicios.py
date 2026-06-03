from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.ejercicio import Ejercicio, EjercicioRead, EjercicioUpdate
from gymguide.Operaciones.ejercicio_OP import *
from gymguide.template_utils import render

router_ejercicios = APIRouter(tags=["Ejercicios"])

# Mostrar ejercicios
@router_ejercicios.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    # Verifica si se deben mostrar inactivos
    showing_inactive = status == "inactive"
    if showing_inactive:
        ejercicios = await showEjercicios(db, include_inactive=True)
        ejercicios = [r for r in ejercicios if r.status == "inactive"]
    else:
        ejercicios = await showEjercicios(db, include_inactive=False)
    # Renderiza la página
    return render("ejercicios.html", {
        "request": request,
        "ejercicios": ejercicios,
        "showing_inactive": showing_inactive
    })

# Vista al detalle
@router_ejercicios.get("/ejercicios/{id}", response_class=HTMLResponse)
async def ejercicio_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
     # Busca el ejercicio por ID
    ej = await showEjercicio_ID(db, id)
    # Retorna error si no existe
    if not ej:
        return HTMLResponse("Ejercicio no encontrado", status_code=404)
    # Obtiene las rutinas asociadas al ejercicio
    rutinas = await get_ejercicio_rutinas(db, id)
    # Renderiza la vista de detalle
    return render("ejercicio_detail.html", {
        "request": request,
        "ej": ej,
        "rutinas": rutinas
    })

# Obtener uno
@router_ejercicios.get("/api/v1/ejercicios/{ejercicio_id}", response_model=EjercicioRead)
async def get_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Busca el ejercicio
    ejercicio = await showEjercicio_ID(db, ejercicio_id)
    # Retorna error si no existe
    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return ejercicio

# Crear
@router_ejercicios.post("/api/v1/ejercicios", response_model=EjercicioRead, status_code=201)
async def create_ejercicio(ejercicio: Ejercicio, db: AsyncSession = Depends(get_db)):
    try:
        # Crea el ejercicio en la BD
        return await createEjercicio(db, ejercicio)
    # Maneja errores de validación
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# actualizar
@router_ejercicios.patch("/api/v1/ejercicios/{ejercicio_id}", response_model=EjercicioRead)
async def update_ejercicio(ejercicio_id: int, data: EjercicioUpdate, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Actualiza el ejercicio
    updated = await updateEjercicio(db, ejercicio_id, data.model_dump(exclude_unset=True))
    # Retorna error si no existe
    if not updated:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return updated

# Eliminar uno
@router_ejercicios.delete("/api/v1/ejercicios/{ejercicio_id}", status_code=204)
async def delete_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Elimina el ejercicio
    deleted = await deleteEjercicio(db, ejercicio_id)
    # Retorna error si no existe
    if not deleted:
        raise HTTPException(status_code=404, detail="Ejercicio not found")

# restaurar 
@router_ejercicios.post("/api/v1/ejercicios/{ejercicio_id}/restore", response_model=EjercicioRead)
async def restore_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Restaura el ejercicio
    restored = await restoreEjercicio(db, ejercicio_id)
    # Retorna error si no existe o ya está activo
    if not restored:
        raise HTTPException(status_code=404, detail="Ejercicio not found or already active")
    return restored
