# --- CRUD asíncrono: Rutinas ---
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from gymguide.models.models_sql import RutinaModel, EjercicioModel, InfluencerModel
from gymguide.models.rutina import Rutina, RutinaID, RutinaUpdate
from gymguide.models.ejercicio import EjercicioID
from gymguide.models.influencer import InfluencerID
from typing import Optional

# --- createRutina: crear registro ---
async def createRutina(db: AsyncSession, rutina: Rutina) -> RutinaID:
    model = RutinaModel(**rutina.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return RutinaID(id=model.id, **rutina.model_dump())

# --- showRutinas: listar con eager load de ejercicios ---
async def showRutinas(db: AsyncSession, include_inactive: bool = False) -> list[RutinaID]:
    query = select(RutinaModel).options(selectinload(RutinaModel.ejercicios))
    if not include_inactive:
        query = query.where(RutinaModel.status == "active")
    result = await db.execute(query.order_by(RutinaModel.id))
    rows = result.scalars().all()
    return [_row_to_id(r) for r in rows]

# --- showRutina_ID: obtener una por ID ---
async def showRutina_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[RutinaID]:
    query = select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == id)
    if not include_inactive:
        query = query.where(RutinaModel.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_id(row) if row else None

# --- updateRutina: actualizar campos ---
async def updateRutina(db: AsyncSession, id: int, data: dict) -> Optional[RutinaID]:
    result = await db.execute(select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)

# --- deleteRutina: soft-delete ---
async def deleteRutina(db: AsyncSession, id: int) -> Optional[Rutina]:
    result = await db.execute(select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return _row_to_rutina(row)

# --- showRutinasLevel: filtrar por nivel ---
async def showRutinasLevel(db: AsyncSession, level: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.level.ilike(level), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- showRutinasObjective: filtrar por objetivo ---
async def showRutinasObjective(db: AsyncSession, objective: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.objective.ilike(objective), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- showRutinasName: buscar por nombre ---
async def showRutinasName(db: AsyncSession, name: str) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.name.ilike(f"%{name}%"), RutinaModel.status == "active").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- showInactiveRutinas: listar solo eliminados ---
async def showInactiveRutinas(db: AsyncSession) -> list[RutinaID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.status == "inactive").order_by(RutinaModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- restoreRutina: reactivar ---
async def restoreRutina(db: AsyncSession, id: int) -> Optional[RutinaID]:
    result = await db.execute(select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == id, RutinaModel.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)

# --- get_rutina_stats: conteos para dashboard ---
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

# --- get_rutina_ejercicios: obtener ejercicios activos de la rutina ---
async def get_rutina_ejercicios(db: AsyncSession, rutina_id: int) -> list[EjercicioID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == rutina_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    return [EjercicioID(
        id=e.id, name=e.name, grupo_muscular=e.grupo_muscular,
        descripcion=e.descripcion or "", series=e.series,
        repeticiones=e.repeticiones, descanso_segundos=e.descanso_segundos,
        image_url=e.image_url or "", status=e.status
    ) for e in (row.ejercicios or []) if e.status == "active"]

# --- get_rutina_influencers: obtener influencers activos que recomiendan esta rutina ---
async def get_rutina_influencers(db: AsyncSession, rutina_id: int) -> list[InfluencerID]:
    result = await db.execute(
        select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(
            InfluencerModel.rutina_recomendada_id == rutina_id, InfluencerModel.status == "active"
        )
    )
    rows = result.scalars().all()
    out = []
    for r in rows:
        rutina_nombre = r.rutina_recomendada.name if r.rutina_recomendada else None
        out.append(InfluencerID(
            id=r.id, name=r.name, categoria=r.categoria,
            logros=r.logros or "", red_social=r.red_social or "",
            rutina_recomendada_id=r.rutina_recomendada_id,
            rutina_recomendada_nombre=rutina_nombre,
            image_url=r.image_url or "", status=r.status
        ))
    return out

# --- set_rutina_ejercicios: reemplazar lista M:N de ejercicios ---
async def set_rutina_ejercicios(db: AsyncSession, id: int, ejercicio_ids: list[int]) -> Optional[RutinaID]:
    result = await db.execute(
        select(RutinaModel).options(selectinload(RutinaModel.ejercicios)).where(RutinaModel.id == id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    if ejercicio_ids:
        ej = await db.execute(select(EjercicioModel).where(EjercicioModel.id.in_(ejercicio_ids)))
        row.ejercicios = list(ej.scalars().all())
    else:
        row.ejercicios = []
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)

# --- _row_to_id: convertir modelo -> Pydantic con IDs de ejercicios ---
def _row_to_id(row: RutinaModel) -> RutinaID:
    ejercicio_ids = [e.id for e in (row.ejercicios or []) if e.status == "active"]
    return RutinaID(
        id=row.id,
        name=row.name,
        level=row.level,
        objective=row.objective,
        duration_weeks=row.duration_weeks,
        ejercicio_ids=ejercicio_ids,
        image_url=row.image_url or "",
        status=row.status
    )

# --- _row_to_rutina: convertir modelo -> Pydantic base (sin relaciones) ---
def _row_to_rutina(row: RutinaModel) -> Rutina:
    return Rutina(
        name=row.name,
        level=row.level,
        objective=row.objective,
        duration_weeks=row.duration_weeks,
        image_url=row.image_url or "",
        status=row.status
    )
