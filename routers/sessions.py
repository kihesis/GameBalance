from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from fastapi.responses import RedirectResponse
from models import GameSession
from schemas import GameSessionCreate
import traceback

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/log")
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})


@router.post("/log")
async def create_session(
        request: Request,
        hours: float = Form(...),
        mood: str = Form(...),
        db: Session = Depends(get_db)

):
    try:
        # Создаем новую сессию
        db_session = GameSession(game_name="Dota 2", hours_played=hours)  # ← используй правильные имена полей
        print(f"DEBUG: Получены данные — hours={hours}, mood={mood}")
        print("DEBUG: Пытаемся сохранить в БД...")
        db.add(db_session)
        db.commit()
        print("DEBUG: Данные успешно сохранены!")
        db.refresh(db_session)


        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        # Логируем ошибку в консоль для отладки
        print("Ошибка при сохранении сессии:")
        print(traceback.format_exc())

        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "❌ Произошла ошибка при сохранении данных. Попробуйте позже."
        })
