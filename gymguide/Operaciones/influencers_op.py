from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from gymguide.models.models_sql import InfluencerModel, RutinaModel, SuplementoModel
from gymguide.models.influencer import Influencer, InfluencerID, InfluencerUpdate
from gymguide.models.suplemento import SuplementoID
from typing import Optional


async def createInfluencer(db: AsyncSession, influencer: Influencer) -> InfluencerID:
    if influencer.rutina_recomendada_id is not None:
        result = await db.execute(select(RutinaModel).where(RutinaModel.id == influencer.rutina_recomendada_id, RutinaModel.status == "active"))
        if not result.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {influencer.rutina_recomendada_id} no existe")
    model = InfluencerModel(**influencer.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return InfluencerID(id=model.id, **influencer.model_dump())


async def showInfluencers(db: AsyncSession, include_inactive: bool = False) -> list[InfluencerID]:
    query = select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada))
    if not include_inactive:
        query = query.where(InfluencerModel.status == "active")
    result = await db.execute(query.order_by(InfluencerModel.id))
    rows = result.scalars().all()
    return [_row_to_id(r) for r in rows]


async def showInfluencer_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[InfluencerID]:
    query = select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(InfluencerModel.id == id)
    if not include_inactive:
        query = query.where(InfluencerModel.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_id(row) if row else None


async def updateInfluencer(db: AsyncSession, id: int, data: dict) -> Optional[InfluencerID]:
    result = await db.execute(select(InfluencerModel).where(InfluencerModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    if "rutina_recomendada_id" in data and data["rutina_recomendada_id"] is not None:
        r = await db.execute(select(RutinaModel).where(RutinaModel.id == data["rutina_recomendada_id"], RutinaModel.status == "active"))
        if not r.scalar_one_or_none():
            raise ValueError(f"La rutina con ID {data['rutina_recomendada_id']} no existe")
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def deleteInfluencer(db: AsyncSession, id: int) -> Optional[Influencer]:
    result = await db.execute(select(InfluencerModel).where(InfluencerModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return _row_to_influencer(row)


async def showInfluencersCategory(db: AsyncSession, categoria: str) -> list[InfluencerID]:
    result = await db.execute(
        select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(InfluencerModel.categoria.ilike(categoria), InfluencerModel.status == "active")
        .order_by(InfluencerModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showInfluencersName(db: AsyncSession, name: str) -> list[InfluencerID]:
    result = await db.execute(
        select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(InfluencerModel.name.ilike(f"%{name}%"), InfluencerModel.status == "active")
        .order_by(InfluencerModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def showInactiveInfluencers(db: AsyncSession) -> list[InfluencerID]:
    result = await db.execute(
        select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(InfluencerModel.status == "inactive").order_by(InfluencerModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]


async def restoreInfluencer(db: AsyncSession, id: int) -> Optional[InfluencerID]:
    result = await db.execute(select(InfluencerModel).options(selectinload(InfluencerModel.rutina_recomendada)).where(InfluencerModel.id == id, InfluencerModel.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)


async def get_influencer_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(InfluencerModel))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    cats = {}
    for r in all_rows:
        if r.status == "active":
            cats[r.categoria] = cats.get(r.categoria, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_category": cats}


async def get_influencer_suplementos(db: AsyncSession, influencer_id: int) -> list[SuplementoID]:
    result = await db.execute(
        select(InfluencerModel).options(selectinload(InfluencerModel.suplementos)).where(InfluencerModel.id == influencer_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    return [SuplementoID(
        id=s.id, name=s.name, type=s.type, brand=s.brand,
        benefits=s.benefits or "", price=s.price,
        image_url=s.image_url or "", status=s.status
    ) for s in (row.suplementos or []) if s.status == "active"]


def _row_to_id(row: InfluencerModel) -> InfluencerID:
    rutina_nombre = row.rutina_recomendada.name if row.rutina_recomendada else None
    return InfluencerID(
        id=row.id,
        name=row.name,
        categoria=row.categoria,
        logros=row.logros or "",
        red_social=row.red_social or "",
        rutina_recomendada_id=row.rutina_recomendada_id,
        rutina_recomendada_nombre=rutina_nombre,
        image_url=row.image_url or "",
        status=row.status
    )


def _row_to_influencer(row: InfluencerModel) -> Influencer:
    return Influencer(
        name=row.name,
        categoria=row.categoria,
        logros=row.logros or "",
        red_social=row.red_social or "",
        rutina_recomendada_id=row.rutina_recomendada_id,
        image_url=row.image_url or "",
        status=row.status
    )
