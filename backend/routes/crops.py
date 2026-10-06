"""Routes for crops, mandis metadata, and system data status."""

from typing import Optional
from fastapi import APIRouter, Query

from backend.services.data_service import get_crops, get_data_status, get_mandis

router = APIRouter(prefix="/api", tags=["Metadata & Status"])


@router.get("/data-status")
def data_status():
    """Returns real-time pipeline status, active source, and record counts."""
    return get_data_status()


@router.get("/crops")
def list_crops():
    """Returns list of monitored commodities with their current market counts."""
    return {"crops": get_crops()}


@router.get("/mandis")
def list_mandis(crop: Optional[str] = Query(None, description="Filter mandis by commodity")):
    """Returns list of monitored mandis, coordinates, and auction cutoffs."""
    return {"mandis": get_mandis(crop=crop)}
