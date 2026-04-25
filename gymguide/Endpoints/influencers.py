from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from gymguide.models.influencer import Influencer,InfluencerID, InfluencerUpdate
from gymguide.Operaciones_CSV.influencers_op import *


router_influencers = APIRouter(prefix="/influencers", tags=["Influencers"])

@router_influencers.get("", response_model=list[Influencer])
async def get_all_influencers():
    influencers=showInfluencers()
    return influencers


@router_influencers.get("/by-category/{category}", response_model=list[Influencer])
async def get_influencers_by_category(category: str):
    return showInfluencersCategory(category)


@router_influencers.get("/{influencer_id}", response_model=Influencer)
async def get_influencer(influencer_id: int):
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
    updated = updateInfluencer(influencer_id, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return updated


@router_influencers.delete("/{influencer_id}", status_code=204)
async def delete_influencer(influencer_id: int):
    deleted = deleteInfluencer(influencer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Influencer not found")