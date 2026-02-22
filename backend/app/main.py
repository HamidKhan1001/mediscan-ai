"""
MediScan AI — FastAPI Backend (Production-Oriented MVP)
Automated Medical Report Generation from Radiological Scans

This module configures the MediScan AI backend service with:
- Lifespan startup/shutdown hooks
- CORS + Trusted Host protection
- Request timing + request ID middleware
- Versioned API router registration
- Health and readiness endpoints
- Enhanced OpenAPI metadata for developer experience

⚠️ Academic / MVP Disclaimer:
This backend is intended for research, education, and portfolio demonstration.
It is not a certified medical device and must not be used for clinical diagnosis.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import analyze, auth, reports
from app.core.config import settings
from app.core.logging import setup_audit_logger

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
APP_NAME = "MediScan AI"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Lifespan (Startup / Shutdown)
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application lifecycle events.

    Startup:
    - Initializes audit logging
    - Logs application boot status

    Shutdown:
    - Logs graceful shutdown message
    """
    logger.info("🩻 %s starting up (v%s)...", APP_NAME, APP_VERSION)

    try:
        setup_audit_logger()
        logger.info("✅ Audit logging initialized successfully.")
    except Exception as exc:
        logger.exception("❌ Failed to initialize audit logger: %s", exc)
        # Continue startup for MVP resilience; production may fail-fast instead.

    yield

    logger.info("🛑 %s shutting down.", APP_NAME)


# -----------------------------------------------------------------------------
# OpenAPI Tags Metadata
# -----------------------------------------------------------------------------
tags_metadata = [
    {"name": "Authentication", "description": "User registration, login, and JWT token flows."},
    {"name": "Analysis", "description": "Medical image upload, AI inference, severity triage, and explainability."},
    {"name": "Reports", "description": "Generated radiology reports, export, and retrieval endpoints."},
    {"name": "Health", "description": "Service health, readiness, and monitoring endpoints."},
]

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Automated Medical Report Generation from Radiological Scans.\n\n"
        "MediScan AI combines Computer Vision, NLP, and Generative AI to produce "
        "structured radiology-style reports from medical images. The API supports "
        "analysis workflows, report generation, and health monitoring.\n\n"
        "⚠️ Research/Educational Use Only — Not for clinical diagnosis."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# -----------------------------------------------------------------------------
# Middleware: Trusted Hosts (basic host-header protection)
# -----------------------------------------------------------------------------
# Use explicit hostnames in production, e.g. ["mediscan-api.yourdomain.com", "*.run.app"]
allowed_hosts = getattr(settings, "ALLOWED_HOSTS", ["*"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# -----------------------------------------------------------------------------
# Middleware: CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Middleware: Request ID + Timing + Basic Access Logging
# -----------------------------------------------------------------------------
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Adds request tracing and timing headers, and logs request/response details.

    Headers added:
    - X-Request-ID
    - X-Process-Time
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Store request ID in request state for downstream handlers if needed
    request.state.request_id = request_id

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(
            "Unhandled exception | request_id=%s method=%s path=%s error=%s",
            request_id,
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            },
        )

    process_time = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    logger.info(
        "HTTP %s %s -> %s | request_id=%s | %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
        process_time,
    )

    return response


# -----------------------------------------------------------------------------
# Router Registration
# -----------------------------------------------------------------------------
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix=API_PREFIX, tags=["Analysis"])
app.include_router(reports.router, prefix=API_PREFIX, tags=["Reports"])


# -----------------------------------------------------------------------------
# Health Endpoints
# -----------------------------------------------------------------------------
@app.get(f"{API_PREFIX}/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Liveness endpoint for monitoring systems (Cloud Run, uptime probes, etc.).
    Confirms the API process is running.
    """
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "environment": getattr(settings, "ENVIRONMENT", "development"),
        "timestamp_unix": int(time.time()),
        "disclaimer": "This service is for research and educational purposes only.",
    }


@app.get(f"{API_PREFIX}/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness endpoint for deployment checks.
    In production, expand this to verify:
    - Database connectivity
    - Object storage access (Azure Blob)
    - Model availability
    - External service credentials
    """
    return {
        "status": "ready",
        "service": APP_NAME,
        "version": APP_VERSION,
        "checks": {
            "api": "ok",
            "audit_logger": "ok",
            # TODO: add real checks for DB / Azure Blob / Model registry
        },
    }
