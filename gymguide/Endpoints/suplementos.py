from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.suplemento import Suplemento, SuplementoID, SuplementoUpdate
from gymguide.models.enums import TipoSuplementoEnum
from gymguide.Operaciones.suplemento_OP import *

router_suplementos = APIRouter(prefix="/suplementos", tags=["Suplementos"])


@router_suplementos.get("", response_model=list[SuplementoID])
async def get_all_suplementos(db: AsyncSession = Depends(get_db)):
    return await showSuplementos(db)


@router_suplementos.get("/deleted", response_model=list[SuplementoID])
async def get_inactive_suplementos(db: AsyncSession = Depends(get_db)):
    return await showInactiveSuplementos(db)


@router_suplementos.get("/by-type/{type}", response_model=list[SuplementoID])
async def get_suplementos_by_type(type: TipoSuplementoEnum, db: AsyncSession = Depends(get_db)):
    return await showSuplementosType(db, type.value)


@router_suplementos.get("/by-name/{name}", response_model=list[SuplementoID])
async def get_suplementos_by_name(name: str, db: AsyncSession = Depends(get_db)):
    return await showSuplementosName(db, name)


@router_suplementos.get("/{suplemento_id}", response_model=SuplementoID)
async def get_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    suplemento = await showSuplemento_ID(db, suplemento_id)
    if not suplemento:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return suplemento


@router_suplementos.post("", response_model=SuplementoID, status_code=201)
async def create_suplemento(suplemento: Suplemento, db: AsyncSession = Depends(get_db)):
    try:
        return await createSuplemento(db, suplemento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_suplementos.patch("/{suplemento_id}", response_model=SuplementoID)
async def update_suplemento(suplemento_id: int, data: SuplementoUpdate, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateSuplemento(db, suplemento_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return updated


@router_suplementos.delete("/{suplemento_id}", status_code=204)
async def delete_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteSuplemento(db, suplemento_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suplemento not found")


@router_suplementos.post("/{suplemento_id}/restore", response_model=SuplementoID)
async def restore_suplemento(suplemento_id: int, db: AsyncSession = Depends(get_db)):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreSuplemento(db, suplemento_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Suplemento not found or already active")
    return restored
