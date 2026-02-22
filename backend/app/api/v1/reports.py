"""Report retrieval endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user

router = APIRouter()


@router.get("/reports/{scan_id}")
async def get_report(scan_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve a previously generated report by scan ID."""
    # In production, fetch from database
    raise HTTPException(status_code=404, detail=f"Report {scan_id} not found in demo mode.")
