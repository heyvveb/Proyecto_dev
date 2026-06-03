# --- CRUD asíncrono: Suplementos ---
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from gymguide.models.models_sql import SuplementoModel, InfluencerModel
from gymguide.models.suplemento import Suplemento, SuplementoID, SuplementoUpdate
from gymguide.models.influencer import InfluencerID
from typing import Optional

# --- createSuplemento: crear registro ---
async def createSuplemento(db: AsyncSession, suplemento: Suplemento) -> SuplementoID:
    model = SuplementoModel(**suplemento.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return SuplementoID(id=model.id, **suplemento.model_dump())

# --- showSuplementos: listar todos ---
async def showSuplementos(db: AsyncSession, include_inactive: bool = False) -> list[SuplementoID]:
    query = select(SuplementoModel)
    if not include_inactive:
        query = query.where(SuplementoModel.status == "active")
    result = await db.execute(query.order_by(SuplementoModel.id))
    rows = result.scalars().all()
    return [_row_to_id(r) for r in rows]

# --- showSuplemento_ID: obtener uno por ID ---
async def showSuplemento_ID(db: AsyncSession, id: int, include_inactive: bool = False) -> Optional[SuplementoID]:
    query = select(SuplementoModel).where(SuplementoModel.id == id)
    if not include_inactive:
        query = query.where(SuplementoModel.status == "active")
    result = await db.execute(query)
    row = result.scalar_one_or_none()
    return _row_to_id(row) if row else None

# --- updateSuplemento: actualizar campos ---
async def updateSuplemento(db: AsyncSession, id: int, data: dict) -> Optional[SuplementoID]:
    result = await db.execute(select(SuplementoModel).where(SuplementoModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        setattr(row, key, val)
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)

# --- deleteSuplemento: soft-delete ---
async def deleteSuplemento(db: AsyncSession, id: int) -> Optional[Suplemento]:
    result = await db.execute(select(SuplementoModel).where(SuplementoModel.id == id))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "inactive"
    await db.commit()
    await db.refresh(row)
    return _row_to_suplemento(row)

# --- showSuplementosType: filtrar por tipo ---
async def showSuplementosType(db: AsyncSession, type: str) -> list[SuplementoID]:
    result = await db.execute(
        select(SuplementoModel).where(SuplementoModel.type.ilike(type), SuplementoModel.status == "active").order_by(SuplementoModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- showSuplementosName: buscar por nombre ---
async def showSuplementosName(db: AsyncSession, name: str) -> list[SuplementoID]:
    result = await db.execute(
        select(SuplementoModel).where(SuplementoModel.name.ilike(f"%{name}%"), SuplementoModel.status == "active").order_by(SuplementoModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- showInactiveSuplementos: listar solo eliminados ---
async def showInactiveSuplementos(db: AsyncSession) -> list[SuplementoID]:
    result = await db.execute(
        select(SuplementoModel).where(SuplementoModel.status == "inactive").order_by(SuplementoModel.id)
    )
    return [_row_to_id(r) for r in result.scalars().all()]

# --- restoreSuplemento: reactivar ---
async def restoreSuplemento(db: AsyncSession, id: int) -> Optional[SuplementoID]:
    result = await db.execute(select(SuplementoModel).where(SuplementoModel.id == id, SuplementoModel.status == "inactive"))
    row = result.scalar_one_or_none()
    if not row:
        return None
    row.status = "active"
    await db.commit()
    await db.refresh(row)
    return _row_to_id(row)

# --- get_suplemento_stats: conteos para dashboard ---
async def get_suplemento_stats(db: AsyncSession) -> dict:
    total = await db.execute(select(SuplementoModel))
    all_rows = total.scalars().all()
    active = sum(1 for r in all_rows if r.status == "active")
    inactive = sum(1 for r in all_rows if r.status == "inactive")
    by_type = {}
    for r in all_rows:
        if r.status == "active":
            by_type[r.type] = by_type.get(r.type, 0) + 1
    return {"total": len(all_rows), "active": active, "inactive": inactive, "by_type": by_type}

# --- get_suplemento_influencers: obtener influencers activos que usan este suplemento ---
# selectinload anidado evita lazy load al acceder a inf.rutina_recomendada.name
async def get_suplemento_influencers(db: AsyncSession, suplemento_id: int) -> list[InfluencerID]:
    result = await db.execute(
        select(SuplementoModel).options(selectinload(SuplementoModel.influencers).selectinload(InfluencerModel.rutina_recomendada)).where(SuplementoModel.id == suplemento_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return []
    out = []
    for inf in (row.influencers or []):
        if inf.status != "active":
            continue
        rutina_nombre = inf.rutina_recomendada.name if inf.rutina_recomendada else None
        out.append(InfluencerID(
            id=inf.id, name=inf.name, categoria=inf.categoria,
            logros=inf.logros or "", red_social=inf.red_social or "",
            rutina_recomendada_id=inf.rutina_recomendada_id,
            rutina_recomendada_nombre=rutina_nombre,
            image_url=inf.image_url or "", status=inf.status
        ))
    return out

# --- _row_to_id: convertir modelo -> Pydantic ---
def _row_to_id(row: SuplementoModel) -> SuplementoID:
    return SuplementoID(
        id=row.id,
        name=row.name,
        type=row.type,
        brand=row.brand,
        benefits=row.benefits or "",
        price=row.price,
        image_url=row.image_url or "",
        status=row.status
    )

# --- _row_to_suplemento: convertir modelo -> Pydantic base ---
def _row_to_suplemento(row: SuplementoModel) -> Suplemento:
    return Suplemento(
        name=row.name,
        type=row.type,
        brand=row.brand,
        benefits=row.benefits or "",
        price=row.price,
        image_url=row.image_url or "",
        status=row.status
    )
