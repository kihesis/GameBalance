from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
from routers import sessions
from datetime import datetime
import uvicorn
from routers import sessions, stats, api

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(sessions.router)
app.include_router(stats.router)
app.include_router(api.router)


# Инициализация БД
def init_db():
    conn = sqlite3.connect('gamebalance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY, timestamp TEXT, hours REAL, mood TEXT)''')
    conn.commit()
    conn.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/log", response_class=HTMLResponse)
async def log_form(request: Request):
    return templates.TemplateResponse("log.html", {"request": request})


@app.post("/log")
async def log_session(
        request: Request,
        hours: float = Form(...),
        mood: str = Form(...)
):
    conn = sqlite3.connect('gamebalance.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (timestamp, hours, mood) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), hours, mood))
    conn.commit()
    conn.close()

    return templates.TemplateResponse("success.html", {
        "request": request,
        "message": "Данные сохранены! Твой баланс важен."
    })


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    conn = sqlite3.connect('gamebalance.db')
    c = conn.cursor()
    c.execute("SELECT AVG(hours), COUNT(*) FROM sessions")
    avg_hours, total_sessions = c.fetchone()
    conn.close()

    return templates.TemplateResponse("stats.html", {
        "request": request,
        "avg_hours": round(avg_hours or 0, 1),
        "total_sessions": total_sessions
    })
@app.get("/timer")
async def timer_page(request: Request):
    return templates.TemplateResponse("timer.html", {"request": request})

@app.get("/tips")
async def tips_page(request: Request):
    return templates.TemplateResponse("tips.html", {"request": request})


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)