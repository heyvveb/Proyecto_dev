from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from gymguide.models.suplemento import Suplemento, SuplementoRead, SuplementoUpdate
from gymguide.models.influencer import Influencer, InfluencerRead
from typing import Optional


def createSuplemento(db: Session, suplemento: Suplemento) -> SuplementoRead:
    model = Suplemento(**suplemento.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return _row_to_read(model)


def showSuplementos(db: Session, include_inactive: bool = False) -> list[SuplementoRead]:
    query = select(Suplemento)
    if not include_inactive:
        query = query.where(Suplemento.status == "active")
    result = db.execute(query.order_by(Suplemento.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


def showSuplemento_ID(db: Session, id: int, include_inactive: bool = False) -> Optional[SuplementoRead]:
    query = select(Suplemento).where(Suplemento.id == id)
    if not include_inactive:
        query = query.where(Suplemento.status == "active")
    result = db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


def updateSuplemento(db: Session, id: int, data: dict) -> Optional[SuplementoRead]:
    result = db.execute(select(Suplemento).where(Suplemento.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def deleteSuplemento(db: Session, id: int) -> Optional[Suplemento]:
    result = db.execute(select(Suplemento).where(Suplemento.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    db.commit()
    db.refresh(row)
    return row


def showSuplementosType(db: Session, type: str) -> list[SuplementoRead]:
    result = db.execute(
        select(Suplemento).where(Suplemento.type.ilike(type), Suplemento.status == "active").order_by(Suplemento.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showSuplementosName(db: Session, name: str) -> list[SuplementoRead]:
    result = db.execute(
        select(Suplemento).where(Suplemento.name.ilike(f"%{name}%"), Suplemento.status == "active").order_by(Suplemento.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showInactiveSuplementos(db: Session) -> list[SuplementoRead]:
    result = db.execute(
        select(Suplemento).where(Suplemento.status == "inactive").order_by(Suplemento.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def restoreSuplemento(db: Session, id: int) -> Optional[SuplementoRead]:
    result = db.execute(select(Suplemento).where(Suplemento.id == id, Suplemento.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def get_suplemento_stats(db: Session) -> dict:
    total = db.execute(select(Suplemento))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    by_type = {}
    for r in all_rows:
        if r.status == "active":
            by_type[r.type] = by_type.get(r.type, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_type": by_type}


def get_suplemento_influencers(db: Session, suplemento_id: int) -> list[InfluencerRead]:
    result = db.execute(
        select(Suplemento).options(selectinload(Suplemento.influencers).selectinload(Influencer.rutina_recomendada)).where(Suplemento.id == suplemento_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    out = []
    for inf in (row.influencers or []):
        if inf.status != "active":
            continue
        rutina_nombre = inf.rutina_recomendada.name if inf.rutina_recomendada else None
        out.append(InfluencerRead(
            id=inf.id, name=inf.name, categoria=inf.categoria,
            logros=inf.logros or "", red_social=inf.red_social or "",
            rutina_recomendada_id=inf.rutina_recomendada_id,
            rutina_recomendada_nombre=rutina_nombre,
            image_url=inf.image_url or "", status=inf.status
        ))
    return out


def _row_to_read(row: Suplemento) -> SuplementoRead:
    return SuplementoRead(
        id=row.id,
        name=row.name,
        type=row.type,
        brand=row.brand,
        benefits=row.benefits or "",
        price=row.price,
        image_url=row.image_url or "",
        status=row.status
    )
