from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from gymguide.models.rutina import Rutina, RutinaRead, RutinaUpdate
from gymguide.models.ejercicio import Ejercicio, EjercicioRead
from gymguide.models.influencer import Influencer, InfluencerRead
from typing import Optional


async def createRutina(db: AsyncSession, rutina: Rutina) -> RutinaRead:
    model = Rutina(**rutina.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return _row_to_read(model)


async def showRutinas(db: AsyncSession, include_inactive: bool = False) -> list[RutinaRead]:
    query = select(Rutina).options(selectinload(Rutina.ejercicios))
    if not include_inactive:
        query = query.where(Rutina.status == "active")
    result = await db.execute(query.order_by(Rutina.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


async def showRutina_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[RutinaRead]:
    query = select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id)
    if not include_inactive:
        query = query.where(Rutina.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


async def updateRutina(db: AsyncSession, id: int, data: dict) -> Optional[RutinaRead]:
    result = await db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_read(row)


async def deleteRutina(db: AsyncSession, id: int) -> Optional[Rutina]:
    result = await db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return row


async def showRutinasLevel(db: AsyncSession, level: str) -> list[RutinaRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.level.ilike(level), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def showRutinasObjective(db: AsyncSession, objective: str) -> list[RutinaRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.objective.ilike(objective), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def showRutinasName(db: AsyncSession, name: str) -> list[RutinaRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.name.ilike(f"%{name}%"), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def showInactiveRutinas(db: AsyncSession) -> list[RutinaRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.status == "inactive").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def restoreRutina(db: AsyncSession, id: int) -> Optional[RutinaRead]:
    result = await db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id, Rutina.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_read(row)


async def get_rutina_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(Rutina))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    by_level = {}
    by_objective = {}
    for r in all_rows:
        if r.status == "active":
            by_level[r.level] = by_level.get(r.level, 0) + 1
            by_objective[r.objective] = by_objective.get(r.objective, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_level": by_level, "by_objective": by_objective}


async def get_rutina_ejercicios(db: AsyncSession, rutina_id: int) -> list[EjercicioRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == rutina_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    return [EjercicioRead(
        id=e.id, name=e.name, grupo_muscular=e.grupo_muscular,
        descripcion=e.descripcion or "", series=e.series,
        repeticiones=e.repeticiones, descanso_segundos=e.descanso_segundos,
        image_url=e.image_url or "", status=e.status
    ) for e in (row.ejercicios or []) if e.status == "active"]


async def get_rutina_influencers(db: AsyncSession, rutina_id: int) -> list[InfluencerRead]:
    result = await db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada)).where(
            Influencer.rutina_recomendada_id == rutina_id, Influencer.status == "active"
        )
    )
    rows = result.scalars().all()
    out = []
    for r in rows:
        rutina_nombre = r.rutina_recomendada.name if r.rutina_recomendada else None
        out.append(InfluencerRead(
            id=r.id, name=r.name, categoria=r.categoria,
            logros=r.logros or "", red_social=r.red_social or "",
            rutina_recomendada_id=r.rutina_recomendada_id,
            rutina_recomendada_nombre=rutina_nombre,
            image_url=r.image_url or "", status=r.status
        ))
    return out


async def set_rutina_ejercicios(db: AsyncSession, id: int, ejercicio_ids: list[int]) -> Optional[RutinaRead]:
    result = await db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    if ejercicio_ids:
        ej = await db.execute(select(Ejercicio).where(Ejercicio.id.in_(ejercicio_ids)))
        row.ejercicios = list(ej.scalars().all())
    else:
        row.ejercicios = []
    await db.commit()
    await db.refresh(row)
    return _row_to_read(row)


def _row_to_read(row: Rutina) -> RutinaRead:
    ejercicio_ids = [e.id for e in (row.ejercicios or []) if e.status == "active"]
    return RutinaRead(
        id=row.id,
        name=row.name,
        level=row.level,
        objective=row.objective,
        duration_weeks=row.duration_weeks,
        ejercicio_ids=ejercicio_ids,
        image_url=row.image_url or "",
        status=row.status
    )
