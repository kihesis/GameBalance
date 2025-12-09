from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routers import sessions, stats, api

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(sessions.router)
app.include_router(stats.router)
app.include_router(api.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/log", response_class=HTMLResponse)
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})

@app.get("/timer")
async def timer_page(request: Request):
    return templates.TemplateResponse("timer.html", {"request": request})

@app.get("/tips")
async def tips_page(request: Request):
    return templates.TemplateResponse("tips.html", {"request": request})