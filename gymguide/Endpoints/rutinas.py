from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from gymguide.models.rutina import Rutina, RutinaID, RutinaUpdate
from gymguide.models.enums import LevelEnum, ObjectiveEnum
from gymguide.Operaciones_CSV.rutina_OP import *


router_rutinas = APIRouter(prefix="/rutinas", tags=["Rutinas"])

@router_rutinas.get("", response_model=list[Rutina])
async def get_all_rutinas():
    rutinas=showRutinas()
    return rutinas


@router_rutinas.get("/deleted", response_model=list[Rutina])
async def get_inactive_rutinas():
    return showInactiveRutinas()


@router_rutinas.get("/by-level/{level}", response_model=list[Rutina])
async def get_rutinas_by_level(level: LevelEnum):
    return showRutinasLevel(level.value)


@router_rutinas.get("/by-objective/{objective}", response_model=list[Rutina])
async def get_rutinas_by_objective(objective: ObjectiveEnum):
    return showRutinasObjective(objective.value)


@router_rutinas.get("/by-name/{name}", response_model=list[Rutina])
async def get_rutinas_by_name(name: str):
    return showRutinasName(name)


@router_rutinas.get("/{rutina_id}", response_model=Rutina)
async def get_rutina(rutina_id: int):
    rutina = showRutina_ID(rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return rutina


@router_rutinas.post("", response_model=Rutina, status_code=201)
async def create_rutina(rutina: Rutina):
    try:
        return createRutina(rutina)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_rutinas.patch("/{rutina_id}", response_model=Rutina)
async def update_rutina(rutina_id: int, data: RutinaUpdate):
    updated = updateRutina(rutina_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return updated


@router_rutinas.delete("/{rutina_id}", status_code=204)
async def delete_rutina(rutina_id: int):
    deleted = deleteRutina(rutina_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rutina not found")


@router_rutinas.post("/{rutina_id}/restore", response_model=Rutina)
async def restore_rutina(rutina_id: int):
    restored = restoreRutina(rutina_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Rutina not found or already active")