from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import GameSession
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import traceback
import re
from uuid import uuid4
from fastapi import Response

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class SessionCreate(BaseModel):
    game_name: str
    hours_played: float
    mood_score: Optional[int] = None

@router.get("/log")
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})

@router.post("/log")
async def create_session_form(
    request: Request,
    response: Response,
    game_name: str = Form(...),
    hours: float = Form(...),
    mood_score: int = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("gamebalance_uid")

    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(
            key="gamebalance_uid",
            value=user_id,
            httponly=False,
            max_age=31536000,
            samesite="lax",
            secure=False
        )
        print(f"Создан новый User ID: {user_id}")

    errors = []
    game_name = game_name.strip()

    if len(game_name) < 2: errors.append("Название мин. 2 символа")
    if len(game_name) > 50: errors.append("Название макс. 50 символов")
    if re.match(r'^[0-9]+$', game_name): errors.append("Название должно содержать буквы")
    if hours < 0.25: errors.append("Мин. время 0.25 ч")
    if hours > 24: errors.append("Макс. время 24 ч")
    if mood_score < 1 or mood_score > 10: errors.append("Настроение 1-10")

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(GameSession).filter(
        GameSession.timestamp >= today_start,
        GameSession.user_id == user_id
    ).all()
    today_total = sum(s.hours_played for s in today_sessions)

    if today_total + hours > 24:
        errors.append(f"Лимит суток превышен! Уже {today_total:.2f}ч.")

    if errors:
        return templates.TemplateResponse("log.html", {
            "request": request,
            "error": "Ошибка: " + "; ".join(errors),
            "game_name": game_name,
            "hours": hours,
            "mood_score": mood_score
        })

    try:
        new_session = GameSession(
            user_id=user_id,
            game_name=game_name,
            hours_played=hours,
            mood_score=mood_score,
            timestamp=datetime.now(timezone.utc)
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        print(f"Запись сохранена: ID={new_session.id}, User={user_id}, Game={game_name}, Hours={hours}")

        return RedirectResponse(url="/stats", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"ОШИБКА БД: {e}")
        print(traceback.format_exc())
        return templates.TemplateResponse("log.html", {
            "request": request,
            "error": f"Ошибка БД: {str(e)}"
        })

@router.post("/api/sessions")
async def create_session_api(request: Request, response: Response, data: SessionCreate, db: Session = Depends(get_db)):
    user_id = request.cookies.get("gamebalance_uid")

    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(
            key="gamebalance_uid",
            value=user_id,
            httponly=False,
            max_age=31536000,
            samesite="lax",
            secure=False
        )

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = db.query(GameSession).filter(
        GameSession.timestamp >= today_start,
        GameSession.user_id == user_id
    ).all()
    today_total = sum(s.hours_played for s in today_sessions)

    if today_total + data.hours_played > 24:
        raise HTTPException(status_code=400, detail=f"Лимит превышен ({today_total:.2f}ч)")

    try:
        new_session = GameSession(
            user_id=user_id,
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
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sessions")
async def get_sessions(request: Request, response: Response, db: Session = Depends(get_db)):
    user_id = request.cookies.get("gamebalance_uid")

    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(
            key="gamebalance_uid",
            value=user_id,
            httponly=False,
            max_age=31536000,
            samesite="lax",
            secure=False
        )

    sessions = db.query(GameSession).filter(
        GameSession.user_id == user_id
    ).order_by(GameSession.timestamp.desc()).all()
    return sessions
