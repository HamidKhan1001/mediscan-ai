"""
MediScan AI — FastAPI Backend
Automated Medical Report Generation from Radiological Scans
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time
import logging

from app.api.v1 import analyze, auth, reports
from app.core.config import settings
from app.core.logging import setup_audit_logger

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🩻 MediScan AI starting up...")
    setup_audit_logger()
    yield
    logger.info("MediScan AI shutting down.")


app = FastAPI(
    title="MediScan AI",
    description="Automated Medical Report Generation from Radiological Scans",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "MediScan AI",
        "version": "1.0.0",
        "disclaimer": "This service is for research and educational purposes only.",
    }
