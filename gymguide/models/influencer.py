from pydantic import BaseModel, Field
from typing import Optional


class Influencer(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    Categoria: str = Field(..., pattern="^(bodybuilding|fitness|powerlifting|crossfit|yoga)$")
    logros: str 
    red_social: str
    rutina_recomendada_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Chris Bumstead",
                "Categoria": "bodybuilding",
                "logros": "Mr. Olympia 2024",
                "red_social": "@cbum",
                "rutina_recomendada_id": 1
            }
        }
class InfluencerID(Influencer):
    id: int = Field(...,gt=0)

class InfluencerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    Categoria: Optional[str] = Field(None, pattern="^(bodybuilding|fitness|powerlifting|crossfit|yoga)$")
    logros: Optional[str] = None
    red_social: Optional[str] = None
    rutina_recomendada_id: Optional[int] = None