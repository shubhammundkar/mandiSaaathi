"""Routes for crops, mandis metadata, and system data status."""

from typing import Optional
from fastapi import APIRouter, Query

from backend.services.data_service import get_crops, get_data_status, get_mandis, get_prices

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


@router.get("/prices")
def list_prices(
    crop: Optional[str] = Query(None, description="Filter by crop name (e.g. Tomato, Onion)"),
    days: Optional[str] = Query(None, description="Number of past days (e.g. 7, 30)")
):
    """Returns historical and current market price records with is_sample indicator."""
    days_val = 30
    if days is not None and str(days).strip():
        try:
            days_val = int(str(days).strip())
        except ValueError:
            days_val = 30
    return get_prices(crop=crop, days=days_val)
