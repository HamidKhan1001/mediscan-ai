"""
MediScan AI — FastAPI Backend
Automated Medical Report Generation from Radiological Scans

This module initializes the FastAPI application for MediScan AI, including:
- Application lifecycle events (startup/shutdown)
- CORS middleware
- Request timing middleware
- API route registration
- Health check endpoint

Project Context:
MediScan AI is a multimodal AI system for generating structured radiology reports
from radiological images (e.g., chest X-rays, MRI scans, retinal images) using:
- Computer Vision (abnormality detection)
- NLP / Generative AI (report synthesis)
- Explainability (Grad-CAM heatmaps)
"""

from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import analyze, auth, reports
from app.core.config import settings
from app.core.logging import setup_audit_logger

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Application Lifespan Events
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the FastAPI application.

    Startup:
    - Initializes audit logging
    - Logs application startup status

    Shutdown:
    - Logs graceful shutdown status
    """
    logger.info("🩻 MediScan AI starting up...")
    setup_audit_logger()
    logger.info("✅ Audit logger initialized.")
    yield
    logger.info("🛑 MediScan AI shutting down.")


# -----------------------------------------------------------------------------
# FastAPI App Initialization
# -----------------------------------------------------------------------------
app = FastAPI(
    title="MediScan AI",
    description=(
        "Automated Medical Report Generation from Radiological Scans.\n\n"
        "This API powers the MediScan AI platform, which performs AI-assisted "
        "medical image analysis and generates structured radiology reports.\n\n"
        "⚠️ Disclaimer: For research and educational purposes only. "
        "Not intended for clinical diagnosis."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# Middleware: CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Frontend origins (React app, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Middleware: Request Processing Time
# -----------------------------------------------------------------------------
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Adds request processing time to response headers.

    Header:
        X-Process-Time: Total request processing time in seconds
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# -----------------------------------------------------------------------------
# API Routers
# -----------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])


# -----------------------------------------------------------------------------
# Health Check Endpoint
# -----------------------------------------------------------------------------
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint for monitoring and deployment readiness.

    Returns:
        dict: Service health information
    """
    return {
        "status": "healthy",
        "service": "MediScan AI",
        "version": "1.0.0",
        "disclaimer": "This service is for research and educational purposes only.",
    }
