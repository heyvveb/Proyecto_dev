from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session
from gymguide.models.influencer import Influencer, InfluencerRead, InfluencerUpdate
from gymguide.models.rutina import Rutina
from gymguide.models.suplemento import Suplemento, SuplementoRead
from typing import Optional


def createInfluencer(db: Session, influencer: Influencer) -> InfluencerRead:
    if influencer.rutina_recomendada_id is not None:
        result = db.execute(select(Rutina).where(Rutina.id == influencer.rutina_recomendada_id, Rutina.status == "active"))
        if not result.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {influencer.rutina_recomendada_id} no existe")
    model = Influencer(**influencer.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return _row_to_read(model)


def showInfluencers(db: Session, include_inactive: bool = False) -> list[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos))
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    result = db.execute(query.order_by(Influencer.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


def showInfluencer_ID(db: Session, id: int, include_inactive: bool = False) -> Optional[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    result = db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


def updateInfluencer(db: Session, id: int, data: dict) -> Optional[InfluencerRead]:
    result = db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    if "rutina_recomendada_id" in data and data["rutina_recomendada_id"] is not None:
        r = db.execute(select(Rutina).where(Rutina.id == data["rutina_recomendada_id"], Rutina.status == "active"))
        if not r.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {data['rutina_recomendada_id']} no existe")
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def deleteInfluencer(db: Session, id: int) -> Optional[Influencer]:
    result = db.execute(select(Influencer).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    db.commit()
    db.refresh(row)
    return row


def showInfluencersCategory(db: Session, categoria: str) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.categoria.ilike(categoria), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showInfluencersName(db: Session, name: str) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.name.ilike(f"%{name}%"), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def showInactiveInfluencers(db: Session) -> list[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.status == "inactive").order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


def restoreInfluencer(db: Session, id: int) -> Optional[InfluencerRead]:
    result = db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id, Influencer.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def get_influencer_stats(db: Session) -> dict:
    total = db.execute(select(Influencer))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    cats = {}
    for r in all_rows:
        if r.status == "active":
            cats[r.categoria] = cats.get(r.categoria, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_category": cats}


def get_influencer_suplementos(db: Session, influencer_id: int) -> list[SuplementoRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.suplementos)).where(Influencer.id == influencer_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    return [SuplementoRead(
        id=s.id, name=s.name, type=s.type, brand=s.brand,
        benefits=s.benefits or "", price=s.price,
        image_url=s.image_url or "", status=s.status
    ) for s in (row.suplementos or []) if s.status == "active"]


def set_influencer_suplementos(db: Session, id: int, suplemento_ids: list[int]) -> Optional[InfluencerRead]:
    result = db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    if suplemento_ids:
        sups = db.execute(select(Suplemento).where(Suplemento.id.in_(suplemento_ids)))
        row.suplementos = list(sups.scalars().all())
    else:
        row.suplementos = []
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def _row_to_read(row: Influencer) -> InfluencerRead:
    rutina_nombre = row.rutina_recomendada.name if row.rutina_recomendada else None
    suplemento_ids = [s.id for s in (row.suplementos or []) if s.status == "active"]
    return InfluencerRead(
        id=row.id,
        name=row.name,
        categoria=row.categoria,
        logros=row.logros or "",
        red_social=row.red_social or "",
        rutina_recomendada_id=row.rutina_recomendada_id,
        rutina_recomendada_nombre=rutina_nombre,
        suplemento_ids=suplemento_ids,
        image_url=row.image_url or "",
        status=row.status
    )
