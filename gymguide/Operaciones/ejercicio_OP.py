from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.models.models_sql import EjercicioModel
from gymguide.models.ejercicio import Ejercicio, EjercicioID, EjercicioUpdate
from typing import Optional


async def createEjercicio(db: AsyncSession, ejercicio: Ejercicio) -> EjercicioID:
    model = EjercicioModel(**ejercicio.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return EjercicioID(id=model.id, **ejercicio.model_dump())


async def showEjercicios(db: AsyncSession, include_inactive: bool = False) -> list[EjercicioID]:
    query = select(EjercicioModel)
    if not include_inactive:
        query = query.where(EjercicioModel.status == "active")
    result = await db.execute(query.order_by(EjercicioModel.id))
    rows = result.scalars().all()
    return [_row_to_id(r) for r in rows]


async def showEjercicio_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[EjercicioID]:
    query = select(EjercicioModel).where(EjercicioModel.id == id)
    if not include_inactive:
        query = query.where(EjercicioModel.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_id(row) if row else None


async def updateEjercicio(db: AsyncSession, id: int, data: dict) -> Optional[EjercicioID]:
    result = await db.execute(select(EjercicioModel).where(EjercicioModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def deleteEjercicio(db: AsyncSession, id: int) -> Optional[Ejercicio]:
    result = await db.execute(select(EjercicioModel).where(EjercicioModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return _row_to_ejercicio(row)


async def showEjerciciosMuscle(db: AsyncSession, muscle: str) -> list[EjercicioID]:
    result = await db.execute(
        select(EjercicioModel).where(EjercicioModel.grupo_muscular.ilike(muscle), EjercicioModel.status == "active").order_by(EjercicioModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showEjerciciosName(db: AsyncSession, name: str) -> list[EjercicioID]:
    result = await db.execute(
        select(EjercicioModel).where(EjercicioModel.name.ilike(f"%{name}%"), EjercicioModel.status == "active").order_by(EjercicioModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showInactiveEjercicios(db: AsyncSession) -> list[EjercicioID]:
    result = await db.execute(
        select(EjercicioModel).where(EjercicioModel.status == "inactive").order_by(EjercicioModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def restoreEjercicio(db: AsyncSession, id: int) -> Optional[EjercicioID]:
    result = await db.execute(select(EjercicioModel).where(EjercicioModel.id == id, EjercicioModel.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def get_ejercicio_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(EjercicioModel))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    by_muscle = {}
    for r in all_rows:
        if r.status == "active":
            by_muscle[r.grupo_muscular] = by_muscle.get(r.grupo_muscular, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_muscle": by_muscle}


def _row_to_id(row: EjercicioModel) -> EjercicioID:
    return EjercicioID(
        id=row.id,
        name=row.name,
        grupo_muscular=row.grupo_muscular,
        descripcion=row.descripcion or "",
        series=row.series,
        repeticiones=row.repeticiones,
        descanso_segundos=row.descanso_segundos,
        image_url=row.image_url or "",
        status=row.status
    )


def _row_to_ejercicio(row: EjercicioModel) -> Ejercicio:
    return Ejercicio(
        name=row.name,
        grupo_muscular=row.grupo_muscular,
        descripcion=row.descripcion or "",
        series=row.series,
        repeticiones=row.repeticiones,
        descanso_segundos=row.descanso_segundos,
        image_url=row.image_url or "",
        status=row.status
    )
