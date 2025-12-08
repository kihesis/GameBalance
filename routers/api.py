from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
from database import get_db
from models import GameSession
from schemas import GameSessionCreate, GameSessionResponse

router = APIRouter(prefix="/api", tags=["tracking"])


# 1. Добавить игровую сессию
@router.post("/sessions", response_model=GameSessionResponse)
def add_game_session(
        session: GameSessionCreate,
        db: Session = Depends(get_db)
):
    # Если время не передано — ставим текущее
    if session.timestamp is None:
        session.timestamp = datetime.now(timezone.utc)

    db_session = GameSession(
        game_name=session.game_name,
        hours_played=session.hours_played,
        timestamp=session.timestamp
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


# 2. Получить статистику за период
@router.get("/stats")
def get_stats(period: str = "day", db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "2weeks":
        start = now - timedelta(weeks=2)
    elif period == "month":
        start = now - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use: day, 2weeks, month")

    sessions = db.query(GameSession).filter(GameSession.timestamp >= start).all()

    total_hours = sum(s.hours_played for s in sessions)
    games = {}
    for s in sessions:
        games[s.game_name] = games.get(s.game_name, 0) + s.hours_played

    return {
        "period": period,
        "total_sessions": len(sessions),
        "total_hours": round(total_hours, 2),
        "games": games,
        "sessions": [
            {
                "id": s.id,
                "game": s.game_name,
                "hours": s.hours_played,
                "timestamp": s.timestamp.isoformat()
            }
            for s in sessions
        ]
    }