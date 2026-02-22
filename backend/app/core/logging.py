"""
HIPAA Audit Logger — §164.312(b)
Logs all API access with timestamp, user, action, IP, and status.
"""

import logging
import json
from datetime import datetime


def setup_audit_logger():
    audit_logger = logging.getLogger("mediscan.audit")
    audit_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    audit_logger.addHandler(handler)


def log_audit_event(
    user_id: str,
    action: str,
    endpoint: str,
    ip_address: str,
    status_code: int,
    scan_id: str = None,
):
    """Write a structured HIPAA audit log entry."""
    audit_logger = logging.getLogger("mediscan.audit")
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "action": action,
        "endpoint": endpoint,
        "ip_address": ip_address,
        "status_code": status_code,
        "scan_id": scan_id,
        "hipaa_ref": "§164.312(b)",
    }
    audit_logger.info(json.dumps(entry))
