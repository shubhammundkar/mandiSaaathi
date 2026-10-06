"""Advisory route handling net return calculation and mandi rankings."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.advisory_engine import calculate_advisory

router = APIRouter(prefix="/api", tags=["Advisory"])


class AdvisoryRequest(BaseModel):
    crop: str = Field(..., example="Tomato")
    district: str = Field(..., example="Pune")
    quantity_quintals: float = Field(20.0, ge=0.1, example=20.0)
    vehicle_type: str = Field("tempo", example="tempo")
    departure_hour: float = Field(7.0, ge=0.0, le=24.0, example=7.0)
    language: Optional[str] = Field("en", example="mr")
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    overrides: Optional[Dict[str, Any]] = None


@router.post("/advise")
def get_recommendation(payload: AdvisoryRequest):
    """Calculates net returns across candidate mandis for the selected crop,

    taking into account transit time, vehicle cost, auction cutoff, and spoilage.
    """
    try:
        result = calculate_advisory(
            crop=payload.crop,
            district=payload.district,
            quantity_quintals=payload.quantity_quintals,
            vehicle_type=payload.vehicle_type,
            departure_hour=payload.departure_hour,
            origin_lat=payload.origin_lat,
            origin_lng=payload.origin_lng,
            overrides=payload.overrides
        )
        if "error" in result and result.get("best_recommendation") is None:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Advisory calculation failed: {str(exc)}")
