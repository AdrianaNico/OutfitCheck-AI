"""
OutfitCheck AI — Main Application
A digital stylist powered by dual AI agents (Gemini + Groq).
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from backend.database import init_db
from backend.config import UPLOAD_DIR

# Import routers
from backend.routers.auth_router import router as auth_router
from backend.routers.wardrobe_router import router as wardrobe_router
from backend.routers.outfit_router import router as outfit_router
from backend.routers.search_router import router as search_router

# Create FastAPI app
app = FastAPI(
    title="OutfitCheck AI",
    description="Your AI-powered fashion assistant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Include API routers
app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(outfit_router)
app.include_router(search_router)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()


# ─── Page Routes ─────────────────────────────

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/outfits")
async def outfits_page(request: Request):
    return templates.TemplateResponse("outfits.html", {"request": request})


@app.get("/critic")
async def critic_page(request: Request):
    return templates.TemplateResponse("critic.html", {"request": request})


@app.get("/search")
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/favorites")
async def favorites_page(request: Request):
    return templates.TemplateResponse("favorites.html", {"request": request})


# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "OutfitCheck AI", "version": "1.0.0"}
