from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.suplemento import Suplemento, SuplementoID, SuplementoUpdate
from gymguide.Operaciones.suplemento_OP import *
from gymguide.template_utils import render

router_suplementos = APIRouter(tags=["Suplementos"])

# listado 
@router_suplementos.get("/suplementos", response_class=HTMLResponse)
async def suplementos_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    # Verifica si se muestran inactivos
    showing_inactive = status == "inactive"
    if showing_inactive:
        suplementos = await showSuplementos(db, include_inactive=True)
        suplementos = [r for r in suplementos if r.status == "inactive"]
    else:
        suplementos = await showSuplementos(db, include_inactive=False)
    # Renderiza la vista
    return render("suplementos.html", {
        "request": request,
        "suplementos": suplementos,
        "showing_inactive": showing_inactive
    })

# Vista detalle 
@router_suplementos.get("/suplementos/{id}", response_class=HTMLResponse)
async def suplemento_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    # Busca el suplemento por ID
    sup = await showSuplemento_ID(db, id)
    # Retorna error si no existe
    if not sup:
        return HTMLResponse("Suplemento no encontrado", status_code=404)
    # Obtiene influencers asociados
    influencers = await get_suplemento_influencers(db, id)
    # Renderiza la vista
    return render("suplemento_detail.html", {
        "request": request,
        "sup": sup,
        "influencers": influencers
    })

# obtener uno 
@router_suplementos.get("/api/v1/suplementos/{suplemento_id}", response_model=SuplementoID)
async def get_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Busca el suplemento
    suplemento = await showSuplemento_ID(db, suplemento_id)
    # Retorna error si no existe
    if not suplemento:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return suplemento

# crear 
@router_suplementos.post("/api/v1/suplementos", response_model=SuplementoID, status_code=201)
async def create_suplemento(suplemento: Suplemento, db: AsyncSession = Depends(get_db)):
    try:
        # Crea el suplemento
        return await createSuplemento(db, suplemento)
        # Maneja errores de validación
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# actualizar 
@router_suplementos.patch("/api/v1/suplementos/{suplemento_id}", response_model=SuplementoID)
async def update_suplemento(suplemento_id: int, data: SuplementoUpdate, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Actualiza el suplemento
    updated = await updateSuplemento(db, suplemento_id, data.model_dump(exclude_unset=True))
    # Retorna error si no existe
    if not updated:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return updated

# eliminar
@router_suplementos.delete("/api/v1/suplementos/{suplemento_id}", status_code=204)
async def delete_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Elimina el suplemento
    deleted = await deleteSuplemento(db, suplemento_id)
    # Retorna error si no existe
    if not deleted:
        raise HTTPException(status_code=404, detail="Suplemento not found")

# restaurar 
@router_suplementos.post("/api/v1/suplementos/{suplemento_id}/restore", response_model=SuplementoID)
async def restore_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    # Valida que el ID sea positivo
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    # Restaura el suplemento
    restored = await restoreSuplemento(db, suplemento_id)
    # Retorna error si no existe o ya está activo
    if not restored:
        raise HTTPException(status_code=404, detail="Suplemento not found or already active")
    return restored
