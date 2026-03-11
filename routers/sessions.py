from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import GameSession
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import traceback
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class SessionCreate(BaseModel):
    game_name: str
    hours_played: float
    mood_score: Optional[int] = None


class SessionResponse(BaseModel):
    id: int
    game_name: str
    hours_played: float
    mood_score: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True


@router.get("/log")
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})


@router.post("/log")
async def create_session_form(
        request: Request,
        game_name: str = Form(...),
        hours: float = Form(...),
        mood_score: int = Form(...),
        db: Session = Depends(get_db)
):
    errors = []

    game_name = game_name.strip()
    if len(game_name) < 2:
        errors.append("Название должно содержать минимум 2 символа")
    if len(game_name) > 50:
        errors.append("Название слишком длинное (максимум 50 символов)")
    if re.match(r'^[0-9]+$', game_name):
        errors.append("Название должно содержать буквы")

    if hours < 0.25:
        errors.append("Минимальное время: 0.25 часа (15 минут)")
    if hours > 24:
        errors.append("Максимальное время: 24 часа")

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(GameSession).filter(
        GameSession.timestamp >= today_start
    ).all()

    today_total = sum(s.hours_played for s in today_sessions)

    if today_total + hours > 24:
        errors.append(f"Превышен лимит времени за сутки! Уже записано {today_total:.2f}ч. Максимум 24 часа в сутки.")

    if mood_score < 1 or mood_score > 10:
        errors.append("Настроение должно быть от 1 до 10")

    if errors:
        return templates.TemplateResponse("log.html", {
            "request": request,
            "error": "Ошибка: " + "; ".join(errors),
            "game_name": game_name,
            "hours": hours,
            "mood_score": mood_score
        })

    try:
        db_session = GameSession(
            game_name=game_name,
            hours_played=hours,
            mood_score=mood_score,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return RedirectResponse(url="/stats", status_code=303)
    except Exception as e:
        print("⚠️Ошибка при сохранении сессии:")
        print(traceback.format_exc())
        return templates.TemplateResponse("log.html", {
            "request": request,
            "error": "⚠️ Ошибка базы данных. Попробуйте позже."
        })


# API (для таймера)
@router.post("/api/sessions")
async def create_session_api(data: SessionCreate, db: Session = Depends(get_db)):
    # Проверка лимита 24 часа
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(GameSession).filter(
        GameSession.timestamp >= today_start
    ).all()

    today_total = sum(s.hours_played for s in today_sessions)

    if today_total + data.hours_played > 24:
        raise HTTPException(
            status_code=400,
            detail=f"Превышен лимит 24 часа за сутки. Уже записано: {today_total:.2f}ч"
        )

    try:
        new_session = GameSession(
            game_name=data.game_name,
            hours_played=data.hours_played,
            mood_score=data.mood_score,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return {"status": "ok", "id": new_session.id}
    except Exception as e:
        print("⚠️API ошибка:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    try:
        sessions = db.query(GameSession).order_by(GameSession.timestamp.desc()).all()
        return sessions
    except Exception as e:
        print("⚠️Ошибка получения сессий:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))