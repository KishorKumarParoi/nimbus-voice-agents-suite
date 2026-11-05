import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from backend.config import settings
from backend.routers import health, agents, voice

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Multi-Agent Voice Suite inspired by Nimbus Voice Agent.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(voice.router)

# Static and HTML Serving
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

if os.path.exists(PUBLIC_DIR):
    css_dir = os.path.join(PUBLIC_DIR, "css")
    js_dir = os.path.join(PUBLIC_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Nimbus Voice Agents Suite</h1><p>API is active. Visit /api/agents</p>")

@app.get("/playground", response_class=HTMLResponse)
async def serve_playground():
    playground_file = os.path.join(PUBLIC_DIR, "playground.html")
    if os.path.exists(playground_file):
        return FileResponse(playground_file)
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))
