"""Advisory route handling net return calculation and mandi rankings."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.advisory_engine import calculate_advisory

router = APIRouter(prefix="/api", tags=["Advisory"])


class AdvisoryRequest(BaseModel):
    crop: str = Field(..., example="Tomato")
    district: Optional[str] = Field("Pune", example="Pune")
    lat: Optional[float] = Field(None, example=18.5204)
    lng: Optional[float] = Field(None, example=73.8567)
    quantity: Optional[float] = Field(None, example=20.0)
    quantity_quintals: Optional[float] = Field(None, example=20.0)
    vehicle: Optional[str] = Field(None, example="tempo")
    vehicle_type: Optional[str] = Field(None, example="tempo")
    departure_hour: float = Field(7.0, ge=0.0, le=24.0, example=7.0)
    language: Optional[str] = Field("en", example="mr")
    overrides: Optional[Dict[str, Any]] = None


@router.post("/advise")
def get_recommendation(payload: AdvisoryRequest):
    """Calculates net returns across candidate mandis for the selected crop,

    taking into account transit time, vehicle cost, auction cutoff, and spoilage.
    """
    try:
        qty = payload.quantity_quintals if payload.quantity_quintals is not None else (payload.quantity if payload.quantity is not None else 20.0)
        veh = payload.vehicle_type if payload.vehicle_type is not None else (payload.vehicle if payload.vehicle is not None else "tempo")

        result = calculate_advisory(
            crop=payload.crop,
            district=payload.district,
            lat=payload.lat,
            lng=payload.lng,
            quantity_quintals=qty,
            vehicle_type=veh,
            departure_hour=payload.departure_hour,
            overrides=payload.overrides
        )
        if "error" in result and result.get("best_recommendation") is None:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Advisory calculation failed: {str(exc)}")
