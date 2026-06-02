from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from gymguide.database import get_db
from gymguide.models.rutina import Rutina, RutinaID, RutinaUpdate
from gymguide.models.enums import LevelEnum, ObjectiveEnum
from gymguide.Operaciones.rutina_OP import *


class EjercicioIdsRequest(BaseModel):
    ejercicio_ids: list[int]

router_rutinas = APIRouter(prefix="/rutinas", tags=["Rutinas"])


@router_rutinas.get("", response_model=list[RutinaID])
async def get_all_rutinas(db: AsyncSession = Depends(get_db)):
    return await showRutinas(db)


@router_rutinas.get("/deleted", response_model=list[RutinaID])
async def get_inactive_rutinas(db: AsyncSession = Depends(get_db)):
    return await showInactiveRutinas(db)


@router_rutinas.get("/by-level/{level}", response_model=list[RutinaID])
async def get_rutinas_by_level(level: LevelEnum, db: AsyncSession = Depends(get_db)):
    return await showRutinasLevel(db, level.value)


@router_rutinas.get("/by-objective/{objective}", response_model=list[RutinaID])
async def get_rutinas_by_objective(objective: ObjectiveEnum, db: AsyncSession = Depends(get_db)):
    return await showRutinasObjective(db, objective.value)


@router_rutinas.get("/by-name/{name}", response_model=list[RutinaID])
async def get_rutinas_by_name(name: str, db: AsyncSession = Depends(get_db)):
    return await showRutinasName(db, name)


@router_rutinas.get("/{rutina_id}", response_model=RutinaID)
async def get_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    rutina = await showRutina_ID(db, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return rutina


@router_rutinas.post("", response_model=RutinaID, status_code=201)
async def create_rutina(rutina: Rutina, db: AsyncSession = Depends(get_db)):
    try:
        return await createRutina(db, rutina)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_rutinas.patch("/{rutina_id}", response_model=RutinaID)
async def update_rutina(rutina_id: int, data: RutinaUpdate, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateRutina(db, rutina_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return updated


@router_rutinas.delete("/{rutina_id}", status_code=204)
async def delete_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteRutina(db, rutina_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rutina not found")


@router_rutinas.put("/{rutina_id}/ejercicios", response_model=RutinaID)
async def set_rutina_ejercicios_endpoint(rutina_id: int, body: EjercicioIdsRequest, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    result = await set_rutina_ejercicios(db, rutina_id, body.ejercicio_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Rutina not found")
    return result


@router_rutinas.post("/{rutina_id}/restore", response_model=RutinaID)
async def restore_rutina(rutina_id: int, db: AsyncSession = Depends(get_db)):
    if rutina_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreRutina(db, rutina_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Rutina not found or already active")
    return restored
