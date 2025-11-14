from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.middleware import AuditLogMiddleware, SecurityHeadersMiddleware
from app.routes import calls, webhooks, health, transcripts
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="DxTx API",
    description="Emotive AI voice agent for patient intake",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add audit logging middleware
app.add_middleware(AuditLogMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(calls.router)
app.include_router(webhooks.router)
app.include_router(transcripts.router)


@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    """
    logger.info("DxTx API starting up...")
    logger.info(f"HIPAA audit logging: {'enabled' if settings.AUDIT_LOG_ENABLED else 'disabled'}")
    logger.info(f"Allowed origins: {settings.allowed_origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    """
    logger.info("DxTx API shutting down...")
    
    # Close transcription and TTS services
    from app.services.transcription import transcription_manager
    from app.services.tts import tts_manager
    
    await transcription_manager.close()
    await tts_manager.close()


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "DxTx - Emotive AI Voice Agent for Patient Intake",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
