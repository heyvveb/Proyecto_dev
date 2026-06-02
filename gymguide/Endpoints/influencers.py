from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from gymguide.database import get_db
from gymguide.models.influencer import Influencer, InfluencerID, InfluencerUpdate
from gymguide.models.enums import CategoriaEnum
from gymguide.Operaciones.influencers_op import *


class SuplementoIdsRequest(BaseModel):
    suplemento_ids: list[int]

router_influencers = APIRouter(prefix="/influencers", tags=["Influencers"])


@router_influencers.get("", response_model=list[InfluencerID])
async def get_all_influencers(db: AsyncSession = Depends(get_db)):
    return await showInfluencers(db)


@router_influencers.get("/deleted", response_model=list[InfluencerID])
async def get_inactive_influencers(db: AsyncSession = Depends(get_db)):
    return await showInactiveInfluencers(db)


@router_influencers.get("/by-category/{category}", response_model=list[InfluencerID])
async def get_influencers_by_category(category: CategoriaEnum, db: AsyncSession = Depends(get_db)):
    return await showInfluencersCategory(db, category.value)


@router_influencers.get("/by-name/{name}", response_model=list[InfluencerID])
async def get_influencers_by_name(name: str, db: AsyncSession = Depends(get_db)):
    return await showInfluencersName(db, name)


@router_influencers.get("/{influencer_id}", response_model=InfluencerID)
async def get_influencer(influencer_id: int, db: AsyncSession = Depends(get_db)):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    influencer = await showInfluencer_ID(db, influencer_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return influencer


@router_influencers.post("", response_model=InfluencerID, status_code=201)
async def create_influencer(influencer: Influencer, db: AsyncSession = Depends(get_db)):
    try:
        return await createInfluencer(db, influencer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_influencers.patch("/{influencer_id}", response_model=InfluencerID)
async def update_influencer(influencer_id: int, data: InfluencerUpdate, db: AsyncSession = Depends(get_db)):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    try:
        updated = await updateInfluencer(db, influencer_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return updated


@router_influencers.delete("/{influencer_id}", status_code=204)
async def delete_influencer(influencer_id: int, db: AsyncSession = Depends(get_db)):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = await deleteInfluencer(db, influencer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Influencer not found")


@router_influencers.put("/{influencer_id}/suplementos", response_model=InfluencerID)
async def set_influencer_suplementos_endpoint(influencer_id: int, body: SuplementoIdsRequest, db: AsyncSession = Depends(get_db)):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    result = await set_influencer_suplementos(db, influencer_id, body.suplemento_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return result


@router_influencers.post("/{influencer_id}/restore", response_model=InfluencerID)
async def restore_influencer(influencer_id: int, db: AsyncSession = Depends(get_db)):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = await restoreInfluencer(db, influencer_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Influencer not found or already active")
    return restored
