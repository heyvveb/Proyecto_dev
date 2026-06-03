from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.suplemento import Suplemento, SuplementoID, SuplementoUpdate
from gymguide.Operaciones.suplemento_OP import *
from gymguide.template_utils import render

router_suplementos = APIRouter(tags=["Suplementos"])

# --- HTML: listado ---
@router_suplementos.get("/suplementos", response_class=HTMLResponse)
async def suplementos_page(request: Request, status: str = "active", db: AsyncSession = Depends(get_db)):
    showing_inactive = status == "inactive"
    if showing_inactive:
        suplementos = await showSuplementos(db, include_inactive=True)
        suplementos = [r for r in suplementos if r.status == "inactive"]
    else:
        suplementos = await showSuplementos(db, include_inactive=False)
    return render("suplementos.html", {
        "request": request,
        "suplementos": suplementos,
        "showing_inactive": showing_inactive
    })

# --- HTML: detalle ---
@router_suplementos.get("/suplementos/{id}", response_class=HTMLResponse)
async def suplemento_detail(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    sup = await showSuplemento_ID(db, id)
    if not sup:
        return HTMLResponse("Suplemento no encontrado", status_code=404)
    influencers = await get_suplemento_influencers(db, id)
    return render("suplemento_detail.html", {
        "request": request,
        "sup": sup,
        "influencers": influencers
    })

# --- JSON: obtener uno ---
@router_suplementos.get("/api/v1/suplementos/{suplemento_id}", response_model=SuplementoID)
async def get_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    suplemento = await showSuplemento_ID(db, suplemento_id)
    if not suplemento:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return suplemento

# --- JSON: crear ---
@router_suplementos.post("/api/v1/suplementos", response_model=SuplementoID, status_code=201)
async def create_suplemento(suplemento: Suplemento, db: AsyncSession = Depends(get_db)):
    try:
        return await createSuplemento(db, suplemento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- JSON: actualizar ---
@router_suplementos.patch("/api/v1/suplementos/{suplemento_id}", response_model=SuplementoID)
async def update_suplemento(suplemento_id: int, data: SuplementoUpdate, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateSuplemento(db, suplemento_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return updated

# --- JSON: eliminar ---
@router_suplementos.delete("/api/v1/suplementos/{suplemento_id}", status_code=204)
async def delete_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteSuplemento(db, suplemento_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suplemento not found")

# --- JSON: restaurar ---
@router_suplementos.post("/api/v1/suplementos/{suplemento_id}/restore", response_model=SuplementoID)
async def restore_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreSuplemento(db, suplemento_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Suplemento not found or already active")
    return restored
