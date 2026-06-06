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

from arlo.core.config import load_settings
from arlo.core.database import init_database
from arlo.api.deps import initialize_services
from arlo.api.schemas import EmailSendRequest
from arlo.services.email_service import EmailService
from arlo.core.config import get_smtp_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_database()
    
    logger.info("Initializing background services...")
    settings = load_settings()
    initialize_services(
        model_path=settings.get("llm_model_path", ""),
        embedding_name=settings.get("embedding_model_name", "")
    )
    
    # Start reminder scheduler in the background if enabled
    if settings.get("reminders_enabled", True):
        try:
            from arlo.features.reminder_engine import ReminderEngine
            smtp = get_smtp_settings()
            email_service = EmailService(
                smtp_server=smtp["server"],
                smtp_port=smtp["port"],
                username=smtp["username"],
                password=smtp["password"],
                sender_email=smtp["sender"]
            )
            reminder_engine = ReminderEngine(email_service)
            reminder_engine.start()
            app.state.reminder_engine = reminder_engine
            logger.info("Background reminder engine scheduler started.")
        except Exception as e:
            logger.warning(f"Could not start background reminder engine: {e}")
            
    yield
    
    # Shutdown reminder engine if running
    if hasattr(app.state, "reminder_engine"):
        try:
            app.state.reminder_engine.scheduler.shutdown()
            logger.info("Background reminder engine scheduler shut down.")
        except Exception:
            pass
    logger.info("Shutting down API...")

app = FastAPI(
    title="Arlo API",
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

# Health endpoint
@app.get("/health")
def health_check():
    from arlo.api.deps import get_llm, get_embedding, get_rag, get_doc_manager
    settings = load_settings()
    return {
        "status": "healthy",
        "llm_loaded": get_llm() is not None and getattr(get_llm(), "is_loaded", False),
        "embedding_loaded": get_embedding() is not None and getattr(get_embedding(), "is_loaded", False),
        "rag_loaded": get_rag() is not None and getattr(get_rag(), "is_initialized", False),
        "doc_manager_loaded": get_doc_manager() is not None,
        "database_path": settings.get("sqlite_db_path")
    }

# Email sending endpoint
@app.post("/email/send")
def api_send_email(payload: EmailSendRequest):
    smtp = get_smtp_settings()
    if not smtp.get("server") or not smtp.get("sender"):
        raise HTTPException(
            status_code=400,
            detail="SMTP settings are not configured. Update settings first."
        )
    service = EmailService(
        smtp_server=smtp["server"],
        smtp_port=smtp["port"],
        username=smtp["username"],
        password=smtp["password"],
        sender_email=smtp["sender"]
    )
    success = service.send_email(
        to_email=payload.to_email,
        subject=payload.subject,
        body_text=payload.body_text,
        body_html=payload.body_html
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email. Check logs and SMTP configuration.")
    return {"status": "success", "message": f"Email successfully sent to {payload.to_email}"}

# Import and include routers
from arlo.api.routers import (
    projects,
    activities,
    blocks,
    communications,
    intentions,
    team,
    reports,
    chat,
    documents,
    settings_
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
