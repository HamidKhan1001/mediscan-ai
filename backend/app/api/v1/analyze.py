"""
/analyze endpoint — core MediScan AI pipeline
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import logging
from datetime import datetime

from app.core.security import get_current_user
from app.models.densenet import get_vision_model
from app.models.biogpt import get_report_generator
from app.services.storage import get_storage_service
from app.services.fhir import generate_fhir_report

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


class ConditionResult(BaseModel):
    name: str
    confidence: float


class ReportSection(BaseModel):
    technique: str
    findings: str
    impression: str
    recommendation: str
    disclaimer: str


class AnalysisResponse(BaseModel):
    scan_id: str
    severity: str
    severity_color: str
    conditions: List[ConditionResult]
    report: ReportSection
    heatmap_url: Optional[str]
    fhir_report_url: Optional[str]
    generated_at: str
    processing_time_ms: float


SEVERITY_COLORS = {
    "URGENT": "#DC2626",   # red-600
    "SEVERE": "#EA580C",   # orange-600
    "MODERATE": "#D97706", # amber-600
    "MILD": "#65A30D",     # lime-600
    "NORMAL": "#16A34A",   # green-600
}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a radiological scan for AI analysis.

    - Accepts JPEG/PNG chest X-rays and MRI slices (max 10MB)
    - Returns 14-pathology detection, severity triage, structured report, and Grad-CAM heatmap URL
    - HIPAA: image anonymised (EXIF stripped), stored encrypted in Azure Blob, auto-deleted after 30 days
    """
    start_time = datetime.utcnow()

    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Accepted: JPEG, PNG",
        )

    image_bytes = await file.read()

    # Validate file size
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size: 10MB")

    scan_id = str(uuid.uuid4())
    logger.info(f"[{scan_id}] Analysis started for user: {current_user['sub']}")

    try:
        # 1. Vision model — pathology detection + Grad-CAM
        vision_model = get_vision_model()
        vision_result = vision_model.predict(image_bytes)

        # 2. Generate Grad-CAM heatmap overlay
        heatmap_png = vision_model.generate_heatmap_overlay(
            image_bytes, vision_result["heatmap"]
        )

        # 3. NLP report generation
        report_gen = get_report_generator()
        report_sections = report_gen.generate_report(
            conditions=vision_result["conditions"],
            severity=vision_result["severity"],
        )

        # 4. Upload heatmap to Azure Blob (encrypted)
        storage = get_storage_service()
        heatmap_url = await storage.upload_bytes(
            data=heatmap_png,
            blob_name=f"{scan_id}/heatmap.png",
            content_type="image/png",
        )

        # 5. Generate FHIR DiagnosticReport
        fhir_report = generate_fhir_report(
            scan_id=scan_id,
            conditions=vision_result["conditions"],
            report_sections=report_sections,
            severity=vision_result["severity"],
        )
        fhir_url = await storage.upload_bytes(
            data=fhir_report.encode(),
            blob_name=f"{scan_id}/report.fhir.json",
            content_type="application/fhir+json",
        )

        processing_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(
            f"[{scan_id}] Analysis complete | severity={vision_result['severity']} | "
            f"top_condition={vision_result['top_condition']} | time={processing_ms:.0f}ms"
        )

        return AnalysisResponse(
            scan_id=scan_id,
            severity=vision_result["severity"],
            severity_color=SEVERITY_COLORS.get(vision_result["severity"], "#16A34A"),
            conditions=vision_result["conditions"],
            report=ReportSection(**report_sections),
            heatmap_url=heatmap_url,
            fhir_report_url=fhir_url,
            generated_at=datetime.utcnow().isoformat(),
            processing_time_ms=processing_ms,
        )

    except Exception as e:
        logger.error(f"[{scan_id}] Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis pipeline failed. Please try again.")
