"""
HL7 FHIR DiagnosticReport formatter for EMR/EHR integration
"""

import json
from datetime import datetime
from typing import Dict, List


def generate_fhir_report(
    scan_id: str,
    conditions: List[Dict],
    report_sections: Dict[str, str],
    severity: str,
) -> str:
    """Generate an HL7 FHIR R4 DiagnosticReport JSON document."""

    observations = [
        {
            "reference": f"Observation/{scan_id}-{i}",
            "display": f"{c['name']}: {c['confidence']:.0%}",
        }
        for i, c in enumerate(conditions[:5])
    ]

    fhir_report = {
        "resourceType": "DiagnosticReport",
        "id": scan_id,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/DiagnosticReport"],
        },
        "status": "preliminary",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "RAD",
                        "display": "Radiology",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "24748-6",
                    "display": "Chest X-ray AP and Lateral",
                }
            ]
        },
        "effectiveDateTime": datetime.utcnow().isoformat() + "Z",
        "issued": datetime.utcnow().isoformat() + "Z",
        "result": observations,
        "conclusion": report_sections.get("impression", ""),
        "conclusionCode": [
            {
                "coding": [
                    {
                        "system": "http://mediscan.ai/severity",
                        "code": severity,
                        "display": f"AI Severity: {severity}",
                    }
                ]
            }
        ],
        "presentedForm": [
            {
                "contentType": "text/plain",
                "title": "AI-Generated Radiology Report",
                "data": _build_text_report(report_sections),
            }
        ],
        "extension": [
            {
                "url": "http://mediscan.ai/disclaimer",
                "valueString": report_sections.get("disclaimer", ""),
            }
        ],
    }

    return json.dumps(fhir_report, indent=2)


def _build_text_report(sections: Dict[str, str]) -> str:
    return (
        f"TECHNIQUE:\n{sections.get('technique', '')}\n\n"
        f"FINDINGS:\n{sections.get('findings', '')}\n\n"
        f"IMPRESSION:\n{sections.get('impression', '')}\n\n"
        f"RECOMMENDATION:\n{sections.get('recommendation', '')}\n\n"
        f"{sections.get('disclaimer', '')}"
    )
