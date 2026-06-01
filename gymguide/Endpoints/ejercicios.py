from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.database import get_db
from gymguide.models.ejercicio import Ejercicio, EjercicioID, EjercicioUpdate
from gymguide.models.enums import GrupoMuscularEnum
from gymguide.Operaciones.ejercicio_OP import *

router_ejercicios = APIRouter(prefix="/ejercicios", tags=["Ejercicios"])


@router_ejercicios.get("", response_model=list[EjercicioID])
async def get_all_ejercicios(db: AsyncSession = Depends(get_db)):
    return await showEjercicios(db)


@router_ejercicios.get("/deleted", response_model=list[EjercicioID])
async def get_inactive_ejercicios(db: AsyncSession = Depends(get_db)):
    return await showInactiveEjercicios(db)


@router_ejercicios.get("/by-muscle/{muscle}", response_model=list[EjercicioID])
async def get_ejercicios_by_muscle(muscle: GrupoMuscularEnum, db: AsyncSession = Depends(get_db)):
    return await showEjerciciosMuscle(db, muscle.value)


@router_ejercicios.get("/by-name/{name}", response_model=list[EjercicioID])
async def get_ejercicios_by_name(name: str, db: AsyncSession = Depends(get_db)):
    return await showEjerciciosName(db, name)


@router_ejercicios.get("/{ejercicio_id}", response_model=EjercicioID)
async def get_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    ejercicio = await showEjercicio_ID(db, ejercicio_id)
    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return ejercicio


@router_ejercicios.post("", response_model=EjercicioID, status_code=201)
async def create_ejercicio(ejercicio: Ejercicio, db: AsyncSession = Depends(get_db)):
    try:
        return await createEjercicio(db, ejercicio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_ejercicios.patch("/{ejercicio_id}", response_model=EjercicioID)
async def update_ejercicio(ejercicio_id: int, data: EjercicioUpdate, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = await updateEjercicio(db, ejercicio_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Ejercicio not found")
    return updated


@router_ejercicios.delete("/{ejercicio_id}", status_code=204)
async def delete_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteEjercicio(db, ejercicio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ejercicio not found")


@router_ejercicios.post("/{ejercicio_id}/restore", response_model=EjercicioID)
async def restore_ejercicio(ejercicio_id: int, db: AsyncSession = Depends(get_db)):
    if ejercicio_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreEjercicio(db, ejercicio_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Ejercicio not found or already active")
    return restored
