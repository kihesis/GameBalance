from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GameSessionCreate(BaseModel):
    game_name: str          # dota2
    hours_played: float = Field(gt=0, le=24)    # Сколько часов за сессию
    timestamp: Optional[datetime] = None

class GameSessionResponse(BaseModel):
    id: int
    game_name: str
    hours_played: float
    timestamp: datetime

    class Config:
        from_attributes = True