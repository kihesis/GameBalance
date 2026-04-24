from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base
from datetime import datetime

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)
    game_name = Column(String(100), nullable=False)
    hours_played = Column(Float, nullable=False)
    mood_score = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.now) # Важно: без timezone.utc
