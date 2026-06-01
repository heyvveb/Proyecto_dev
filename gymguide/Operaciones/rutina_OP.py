from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from gymguide.models.models_sql import RutinaModel
from gymguide.models.rutina import Rutina, RutinaID, RutinaUpdate
from typing import Optional


async def createRutina(db: AsyncSession, rutina: Rutina) -> RutinaID:
    model = RutinaModel(**rutina.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return RutinaID(id=model.id, **rutina.model_dump())


async def showRutinas(db: AsyncSession, include_inactive: bool = False) -> list[RutinaID]:
    query = select(RutinaModel)
    if not include_inactive:
        query = query.where(RutinaModel.status == "active")
    result = await db.execute(query.order_by(RutinaModel.id))
    rows = result.scalars().all()
    return [_row_to_id(r) for r in rows]


async def showRutina_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[RutinaID]:
    query = select(RutinaModel).where(RutinaModel.id == id)
    if not include_inactive:
        query = query.where(RutinaModel.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_id(row) if row else None


async def updateRutina(db: AsyncSession, id: int, data: dict) -> Optional[RutinaID]:
    result = await db.execute(select(RutinaModel).where(RutinaModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def deleteRutina(db: AsyncSession, id: int) -> Optional[Rutina]:
    result = await db.execute(select(RutinaModel).where(RutinaModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return _row_to_rutina(row)


async def showRutinasLevel(db: AsyncSession, level: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).where(RutinaModel.level.ilike(level), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showRutinasObjective(db: AsyncSession, objective: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).where(RutinaModel.objective.ilike(objective), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showRutinasName(db: AsyncSession, name: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).where(RutinaModel.name.ilike(f"%{name}%"), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showInactiveRutinas(db: AsyncSession) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).where(RutinaModel.status == "inactive").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def restoreRutina(db: AsyncSession, id: int) -> Optional[RutinaID]:
    result = await db.execute(select(RutinaModel).where(RutinaModel.id == id, RutinaModel.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def get_rutina_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(RutinaModel))
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


def _row_to_id(row: RutinaModel) -> RutinaID:
    return RutinaID(
        id=row.id,
        name=row.name,
        level=row.level,
        objective=row.objective,
        duration_weeks=row.duration_weeks,
        image_url=row.image_url or "",
        status=row.status
    )


def _row_to_rutina(row: RutinaModel) -> Rutina:
    return Rutina(
        name=row.name,
        level=row.level,
        objective=row.objective,
        duration_weeks=row.duration_weeks,
        image_url=row.image_url or "",
        status=row.status
    )
