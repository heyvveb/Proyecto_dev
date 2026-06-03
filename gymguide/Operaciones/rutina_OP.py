from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from gymguide.models.rutina import Rutina, RutinaRead, RutinaUpdate
from gymguide.models.ejercicio import Ejercicio, EjercicioRead
from gymguide.models.influencer import Influencer, InfluencerRead
from typing import Optional


def createRutina(db: Session, rutina: Rutina) -> RutinaRead:
    model = Rutina(**rutina.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return _row_to_read(model)


def showRutinas(db: Session, include_inactive: bool = False) -> list[RutinaRead]:
    query = select(Rutina).options(selectinload(Rutina.ejercicios))
    if not include_inactive:
        query = query.where(Rutina.status == "active")
    result = db.execute(query.order_by(Rutina.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


def showRutina_ID(db: Session, id: int, include_inactive: bool = False) -> Optional[RutinaRead]:
    query = select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id)
    if not include_inactive:
        query = query.where(Rutina.status == "active")
    result = db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


def updateRutina(db: Session, id: int, data: dict) -> Optional[RutinaRead]:
    result = db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def deleteRutina(db: Session, id: int) -> Optional[Rutina]:
    result = db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    db.commit()
    db.refresh(row)
    return row


def showRutinasLevel(db: Session, level: str) -> list[RutinaRead]:
    result = db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.level.ilike(level), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showRutinasObjective(db: Session, objective: str) -> list[RutinaRead]:
    result = db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.objective.ilike(objective), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showRutinasName(db: Session, name: str) -> list[RutinaRead]:
    result = db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.name.ilike(f"%{name}%"), Rutina.status == "active").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showInactiveRutinas(db: Session) -> list[RutinaRead]:
    result = db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.status == "inactive").order_by(Rutina.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def restoreRutina(db: Session, id: int) -> Optional[RutinaRead]:
    result = db.execute(select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id, Rutina.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def get_rutina_stats(db: Session) -> dict:
    total = db.execute(select(Rutina))
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


def get_rutina_ejercicios(db: Session, rutina_id: int) -> list[EjercicioRead]:
    result = db.execute(
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


def get_rutina_influencers(db: Session, rutina_id: int) -> list[InfluencerRead]:
    result = db.execute(
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


def set_rutina_ejercicios(db: Session, id: int, ejercicio_ids: list[int]) -> Optional[RutinaRead]:
    result = db.execute(
        select(Rutina).options(selectinload(Rutina.ejercicios)).where(Rutina.id == id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    if ejercicio_ids:
        ej = db.execute(select(Ejercicio).where(Ejercicio.id.in_(ejercicio_ids)))
        row.ejercicios = list(ej.scalars().all())
    else:
        row.ejercicios = []
    db.commit()
    db.refresh(row)
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
