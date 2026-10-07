"""API Routes for price forecasting and sell-or-store decision advisory."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.services.forecast_engine import forecast_5_days, get_storage_advice

router = APIRouter(prefix="/api", tags=["Forecasting & Storage"])


@router.get("/forecast")
def get_price_forecast(
    crop: str = Query(..., description="Crop/Commodity name (e.g. Tomato, Soybean)"),
    market: str = Query(..., description="APMC Market name (e.g. Pune, Latur)")
):
    """Returns a 5-day price corridor (Low, Likely, High) using moving average,

    trend momentum, and weekday seasonality adjustments.
    """
    try:
        result = forecast_5_days(crop=crop, market=market)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forecast calculation failed: {str(exc)}")


@router.get("/storage-advice")
def get_crop_storage_advice(
    crop: str = Query(..., description="Crop/Commodity name (e.g. Onion, Soybean, Potato)"),
    market: Optional[str] = Query(None, description="Optional APMC market name")
):
    """Evaluates whether to sell today or store for up to 5 days, subtracting

    warehouse storage rent and quality/moisture shrinkage.
    Returns 'Sell now', 'Wait X days', or 'Not enough data'.
    """
    try:
        result = get_storage_advice(crop=crop, market=market)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Storage advice failed: {str(exc)}")
