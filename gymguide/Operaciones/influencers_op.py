from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from gymguide.models.influencer import Influencer, InfluencerRead, InfluencerUpdate
from gymguide.models.rutina import Rutina
from gymguide.models.suplemento import Suplemento, SuplementoRead
from typing import Optional


async def createInfluencer(db: AsyncSession, influencer: Influencer) -> InfluencerRead:
    if influencer.rutina_recomendada_id is not None:
        result = await db.execute(select(Rutina).where(Rutina.id == influencer.rutina_recomendada_id, Rutina.status == "active"))
        if not result.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {influencer.rutina_recomendada_id} no existe")
    model = Influencer(**influencer.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return _row_to_read(model)


async def showInfluencers(db: AsyncSession, include_inactive: bool = False) -> list[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos))
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    result = await db.execute(query.order_by(Influencer.id))
    rows = result.scalars().all()
    return [_row_to_read(r) for r in rows]


async def showInfluencer_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[InfluencerRead]:
    query = select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    if not include_inactive:
        query = query.where(Influencer.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_read(row) if row else None


async def updateInfluencer(db: AsyncSession, id: int, data: dict) -> Optional[InfluencerRead]:
    result = await db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    if "rutina_recomendada_id" in data and data["rutina_recomendada_id"] is not None:
        r = await db.execute(select(Rutina).where(Rutina.id == data["rutina_recomendada_id"], Rutina.status == "active"))
        if not r.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {data['rutina_recomendada_id']} no existe")
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_read(row)


async def deleteInfluencer(db: AsyncSession, id: int) -> Optional[Influencer]:
    result = await db.execute(select(Influencer).where(Influencer.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return row


async def showInfluencersCategory(db: AsyncSession, categoria: str) -> list[InfluencerRead]:
    result = await db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.categoria.ilike(categoria), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def showInfluencersName(db: AsyncSession, name: str) -> list[InfluencerRead]:
    result = await db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.name.ilike(f"%{name}%"), Influencer.status == "active")
        .order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def showInactiveInfluencers(db: AsyncSession) -> list[InfluencerRead]:
    result = await db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.status == "inactive").order_by(Influencer.id)
    )
    return [_row_to_read(r) for r in result.scalars().all()]


async def restoreInfluencer(db: AsyncSession, id: int) -> Optional[InfluencerRead]:
    result = await db.execute(select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id, Influencer.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_read(row)


async def get_influencer_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(Influencer))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    cats = {}
    for r in all_rows:
        if r.status == "active":
            cats[r.categoria] = cats.get(r.categoria, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_category": cats}


async def get_influencer_suplementos(db: AsyncSession, influencer_id: int) -> list[SuplementoRead]:
    result = await db.execute(
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


async def set_influencer_suplementos(db: AsyncSession, id: int, suplemento_ids: list[int]) -> Optional[InfluencerRead]:
    result = await db.execute(
        select(Influencer).options(selectinload(Influencer.rutina_recomendada), selectinload(Influencer.suplementos)).where(Influencer.id == id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    if suplemento_ids:
        sups = await db.execute(select(Suplemento).where(Suplemento.id.in_(suplemento_ids)))
        row.suplementos = list(sups.scalars().all())
    else:
        row.suplementos = []
    await db.commit()
    await db.refresh(row)
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
