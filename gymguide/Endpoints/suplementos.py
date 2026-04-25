from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from gymguide.models.suplemento import Suplemento, SuplementoID, SuplementoUpdate
from gymguide.models.enums import TipoSuplementoEnum
from gymguide.Operaciones_CSV.suplemento_OP import *


router_suplementos = APIRouter(prefix="/suplementos", tags=["Suplementos"])

@router_suplementos.get("", response_model=list[Suplemento])
async def get_all_suplementos():
    suplementos=showSuplementos()
    return suplementos



@router_suplementos.get("/deleted", response_model=list[Suplemento])
async def get_inactive_suplementos():
    return showInactiveSuplementos()


@router_suplementos.get("/by-type/{type}", response_model=list[Suplemento])
async def get_suplementos_by_type(type: TipoSuplementoEnum):
    return showSuplementosType(type.value)


@router_suplementos.get("/by-name/{name}", response_model=list[Suplemento])
async def get_suplementos_by_name(name: str):
    return showSuplementosName(name)


@router_suplementos.get("/{suplemento_id}", response_model=Suplemento)
async def get_suplemento(suplemento_id: int):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    suplemento = showSuplemento_ID(suplemento_id)
    if not suplemento:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return suplemento


@router_suplementos.post("", response_model=Suplemento, status_code=201)
async def create_suplemento(suplemento: Suplemento):
    try:
        return createSuplemento(suplemento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_suplementos.patch("/{suplemento_id}", response_model=Suplemento)
async def update_suplemento(suplemento_id: int, data: SuplementoUpdate):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = updateSuplemento(suplemento_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Suplemento not found")
    return updated


@router_suplementos.delete("/{suplemento_id}", status_code=204)
async def delete_suplemento(suplemento_id: int):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = deleteSuplemento(suplemento_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suplemento not found")


@router_suplementos.post("/{suplemento_id}/restore", response_model=Suplemento)
async def restore_suplemento(suplemento_id: int):
    if suplemento_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = restoreSuplemento(suplemento_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Suplemento not found or already active")