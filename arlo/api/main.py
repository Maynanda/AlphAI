"""
FastAPI application entry point for Arlo.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root before anything else
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from arlo.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing scheduler, but don't break if apscheduler is missing
try:
    from arlo.services.scheduler import start_scheduler, stop_scheduler
    HAS_SCHEDULER = True
except ImportError:
    HAS_SCHEDULER = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB by getting connection once
    from arlo.api.deps import get_db
    try:
        await get_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")

    if HAS_SCHEDULER and settings.reminders_enabled:
        try:
            await start_scheduler()
            logger.info("Background scheduler started.")
        except Exception as e:
            logger.warning(f"Failed to start scheduler: {e}")
            
    yield
    
    if HAS_SCHEDULER and settings.reminders_enabled:
        try:
            await stop_scheduler()
            logger.info("Background scheduler stopped.")
        except Exception as e:
            logger.warning(f"Failed to stop scheduler: {e}")

app = FastAPI(
    title="Arlo — AlphaAI API",
    description="Backend API for Arlo AI Chief of Staff",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    from arlo.services.llm.provider import get_provider
    provider = get_provider()
    return {
        "status": "healthy",
        "llm_provider": provider.__class__.__name__ if provider else None,
        "database_path": settings.db_path
    }

# Import and include routers
try:
    from arlo.api.routers import (
        projects, activities, blocks, communications, intentions,
        team, reports, chat, documents, settings_
    )
    
    app.include_router(projects.router)
    app.include_router(activities.router)
    app.include_router(blocks.router)
    app.include_router(communications.router)
    app.include_router(intentions.router)
    app.include_router(team.router)
    app.include_router(reports.router)
    app.include_router(chat.router)
    app.include_router(documents.router)
    app.include_router(settings_.router)
except ImportError as e:
    logger.warning(f"Some routers could not be loaded: {e}")
