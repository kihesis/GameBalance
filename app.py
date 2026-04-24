from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from routers import sessions, stats, api
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(sessions.router)
app.include_router(stats.router)
app.include_router(api.router)

@app.on_event("startup")
def set_cookie_on_startup():
    pass

def ensure_cookie(request: Request, response: Response):
    user_id = request.cookies.get("gamebalance_uid")
    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(
            key="gamebalance_uid",
            value=user_id,
            httponly=False, # Поменял на False для отладки, чтобы JS видел (опционально)
            max_age=31536000,
            samesite="none", # Важно для локальных тестов иногда, или оставь lax
            secure=False # Для localhost нужно False
        )
    return user_id

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, response: Response):
    ensure_cookie(request, response)
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/log", response_class=HTMLResponse)
async def log_page(request: Request, response: Response):
    ensure_cookie(request, response)
    return templates.TemplateResponse("log.html", {"request": request})

@app.get("/timer", response_class=HTMLResponse)
async def timer_page(request: Request, response: Response):
    ensure_cookie(request, response)
    return templates.TemplateResponse("timer.html", {"request": request})

@app.get("/tips", response_class=HTMLResponse)
async def tips_page(request: Request, response: Response):
    ensure_cookie(request, response)
    return templates.TemplateResponse("tips.html", {"request": request})
