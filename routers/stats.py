from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import func
from models import GameSession

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/stats")
async def get_stats(request: Request, db: Session = Depends(get_db)):
    avg_hours = db.query(func.avg(GameSession.hours_played)).scalar() or 0
    total_sessions = db.query(GameSession).count()

    return templates.TemplateResponse("stats.html", {
        "request": request,
        "avg_hours": round(avg_hours, 1),
        "total_sessions": total_sessions
    })