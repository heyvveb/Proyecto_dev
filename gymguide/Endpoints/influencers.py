from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from gymguide.models.influencer import Influencer,InfluencerID, InfluencerUpdate
from gymguide.models.enums import CategoriaEnum
from gymguide.Operaciones_CSV.influencers_op import *


router_influencers = APIRouter(prefix="/influencers", tags=["Influencers"])

@router_influencers.get("", response_model=list[Influencer])
async def get_all_influencers():
    influencers=showInfluencers()
    return influencers


@router_influencers.get("/deleted", response_model=list[Influencer])
async def get_inactive_influencers():
    return showInactiveInfluencers()


@router_influencers.get("/by-category/{category}", response_model=list[Influencer])
async def get_influencers_by_category(category: CategoriaEnum):
    return showInfluencersCategory(category.value)


@router_influencers.get("/by-name/{name}", response_model=list[Influencer])
async def get_influencers_by_name(name: str):
    return showInfluencersName(name)


@router_influencers.get("/{influencer_id}", response_model=Influencer)
async def get_influencer(influencer_id: int):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    influencer = showInfluencer_ID(influencer_id)
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return influencer


@router_influencers.post("", response_model=Influencer, status_code=201)
async def create_influencer(influencer: Influencer):
    try:
        return createInfluencer(influencer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_influencers.patch("/{influencer_id}", response_model=Influencer)
async def update_influencer(influencer_id: int, data: InfluencerUpdate):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    updated = updateInfluencer(influencer_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return updated


@router_influencers.delete("/{influencer_id}", status_code=204)
async def delete_influencer(influencer_id: int):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    deleted = deleteInfluencer(influencer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Influencer not found")


@router_influencers.post("/{influencer_id}/restore", response_model=Influencer)
async def restore_influencer(influencer_id: int):
    if influencer_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be a positive integer")
    restored = restoreInfluencer(influencer_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Influencer not found or already active")