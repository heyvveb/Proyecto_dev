from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from gymguide.models.ejercicio import Ejercicio, EjercicioRead, EjercicioUpdate
from gymguide.models.rutina import Rutina, RutinaRead
from typing import Optional


def createEjercicio(db: Session, ejercicio: Ejercicio) -> EjercicioRead:
    model = Ejercicio(**ejercicio.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return _row_to_read(model)


def showEjercicios(db: Session, include_inactive: bool = False) -> list[EjercicioRead]:
    query = select(Ejercicio)
    if not include_inactive:
        query = query.where(Ejercicio.status == "active")
    result = db.execute(query.order_by(Ejercicio.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


def showEjercicio_ID(db: Session, id: int, include_inactive: bool = False) -> Optional[EjercicioRead]:
    query = select(Ejercicio).where(Ejercicio.id == id)
    if not include_inactive:
        query = query.where(Ejercicio.status == "active")
    result = db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


def updateEjercicio(db: Session, id: int, data: dict) -> Optional[EjercicioRead]:
    result = db.execute(select(Ejercicio).where(Ejercicio.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def deleteEjercicio(db: Session, id: int) -> Optional[Ejercicio]:
    result = db.execute(select(Ejercicio).where(Ejercicio.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    db.commit()
    db.refresh(row)
    return row


def showEjerciciosMuscle(db: Session, muscle: str) -> list[EjercicioRead]:
    result = db.execute(
        select(Ejercicio).where(Ejercicio.grupo_muscular.ilike(muscle), Ejercicio.status == "active").order_by(Ejercicio.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showEjerciciosName(db: Session, name: str) -> list[EjercicioRead]:
    result = db.execute(
        select(Ejercicio).where(Ejercicio.name.ilike(f"%{name}%"), Ejercicio.status == "active").order_by(Ejercicio.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showInactiveEjercicios(db: Session) -> list[EjercicioRead]:
    result = db.execute(
        select(Ejercicio).where(Ejercicio.status == "inactive").order_by(Ejercicio.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def restoreEjercicio(db: Session, id: int) -> Optional[EjercicioRead]:
    result = db.execute(select(Ejercicio).where(Ejercicio.id == id, Ejercicio.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def get_ejercicio_stats(db: Session) -> dict:
    total = db.execute(select(Ejercicio))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    by_muscle = {}
    for r in all_rows:
        if r.status == "active":
            by_muscle[r.grupo_muscular] = by_muscle.get(r.grupo_muscular, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_muscle": by_muscle}


def get_ejercicio_rutinas(db: Session, ejercicio_id: int) -> list[RutinaRead]:
    result = db.execute(
        select(Ejercicio).options(selectinload(Ejercicio.rutinas)).where(Ejercicio.id == ejercicio_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    return [RutinaRead(
        id=r.id, name=r.name, level=r.level,
        objective=r.objective, duration_weeks=r.duration_weeks,
        image_url=r.image_url or "", status=r.status
    ) for r in (row.rutinas or []) if r.status == "active"]


def _row_to_read(row: Ejercicio) -> EjercicioRead:
    return EjercicioRead(
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
