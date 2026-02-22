"""
MediScan AI — Backend Unit Tests
pytest + pytest-asyncio + httpx
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from PIL import Image

from app.main import app

client = TestClient(app)


# ─── Health Check ────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MediScan AI"
    assert "disclaimer" in data


# ─── Auth ────────────────────────────────────────────────────────────────────

def test_analyze_requires_auth():
    """Endpoint must reject requests without a Bearer token."""
    img = _create_test_image()
    response = client.post("/api/v1/analyze", files={"file": ("test.jpg", img, "image/jpeg")})
    assert response.status_code == 403


def test_analyze_rejects_invalid_file_type():
    """Non-image file types must be rejected with 415."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": "test-user", "role": "clinician"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("report.pdf", b"PDF content", "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 415


# ─── Vision Model Mocked ─────────────────────────────────────────────────────

@patch("app.api.v1.analyze.get_vision_model")
@patch("app.api.v1.analyze.get_report_generator")
@patch("app.api.v1.analyze.get_storage_service")
def test_analyze_success(mock_storage, mock_report_gen, mock_vision):
    """Full pipeline returns expected response shape with mocked models."""
    from app.core.security import create_access_token
    import numpy as np

    # Mock vision model
    mock_vm = MagicMock()
    mock_vm.predict.return_value = {
        "conditions": [
            {"name": "Pneumonia", "confidence": 0.87},
            {"name": "Pleural Effusion", "confidence": 0.43},
        ],
        "severity": "URGENT",
        "heatmap": np.zeros((224, 224)),
        "top_condition": "Pneumonia",
    }
    mock_vm.generate_heatmap_overlay.return_value = b"fake-png-bytes"
    mock_vision.return_value = mock_vm

    # Mock report generator
    mock_rg = MagicMock()
    mock_rg.generate_report.return_value = {
        "technique": "PA chest X-ray.",
        "findings": "Opacity in right lower lobe.",
        "impression": "Findings consistent with Pneumonia.",
        "recommendation": "URGENT: Immediate clinical review.",
        "disclaimer": "For research use only.",
    }
    mock_report_gen.return_value = mock_rg

    # Mock storage
    mock_ss = MagicMock()
    mock_ss.upload_bytes = MagicMock(return_value="https://storage.azure.com/fake")
    mock_storage.return_value = mock_ss

    token = create_access_token({"sub": "test-user", "role": "clinician"})
    headers = {"Authorization": f"Bearer {token}"}
    img = _create_test_image()

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("xray.jpg", img, "image/jpeg")},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["severity"] == "URGENT"
    assert len(data["conditions"]) == 2
    assert "report" in data
    assert "findings" in data["report"]


# ─── FHIR Output ─────────────────────────────────────────────────────────────

def test_fhir_report_structure():
    """FHIR DiagnosticReport must contain required FHIR R4 fields."""
    from app.services.fhir import generate_fhir_report
    import json

    fhir_json = generate_fhir_report(
        scan_id="test-scan-123",
        conditions=[{"name": "Pneumonia", "confidence": 0.87}],
        report_sections={
            "technique": "PA chest X-ray",
            "findings": "Opacity noted",
            "impression": "Consistent with pneumonia",
            "recommendation": "Urgent review",
            "disclaimer": "Research only",
        },
        severity="URGENT",
    )

    report = json.loads(fhir_json)
    assert report["resourceType"] == "DiagnosticReport"
    assert report["status"] == "preliminary"
    assert "conclusion" in report
    assert "presentedForm" in report


# ─── Severity Classification ──────────────────────────────────────────────────

def test_severity_urgent_for_pneumothorax():
    from app.models.densenet import MediScanVisionModel
    model = MediScanVisionModel.__new__(MediScanVisionModel)
    severity = model._classify_severity([
        {"name": "Pneumothorax", "confidence": 0.75},
    ])
    assert severity == "URGENT"


def test_severity_normal_when_no_conditions():
    from app.models.densenet import MediScanVisionModel
    model = MediScanVisionModel.__new__(MediScanVisionModel)
    severity = model._classify_severity([])
    assert severity == "NORMAL"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _create_test_image() -> bytes:
    """Create a minimal grayscale JPEG for testing."""
    img = Image.new("L", (224, 224), color=128)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()
