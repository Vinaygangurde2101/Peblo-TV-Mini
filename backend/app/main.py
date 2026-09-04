from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.health import router as health_router
from app.api.admin.auth import router as auth_router
from app.api.admin.artwork import router as artwork_router
from app.api.admin.shows import router as shows_router
from app.api.admin.seasons import router as seasons_router
from app.api.admin.episodes import router as episodes_router
from app.api.admin.validation import router as validation_router
from app.api.admin.publishing import router as publishing_router
from app.api.catalogue.routes import router as catalogue_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage directories exist
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
artwork_dir = os.path.join(settings.STORAGE_PATH, "artwork")
os.makedirs(artwork_dir, exist_ok=True)

# Static file serving for artwork in local dev
app.mount("/static/artwork", StaticFiles(directory=artwork_dir), name="artwork_static")

# Include Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(artwork_router)
app.include_router(shows_router)
app.include_router(seasons_router)
app.include_router(episodes_router)
app.include_router(validation_router)
app.include_router(publishing_router)
app.include_router(catalogue_router)








@app.get("/")
def read_root():
    return {"message": "Welcome to Peblo TV Mini API", "docs": "/docs"}
