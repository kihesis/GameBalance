from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base
from datetime import datetime, timezone


class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String(100), nullable=False)
    hours_played = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))