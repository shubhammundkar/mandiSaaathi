"""API Routes for the 90-Day Backtest Historical Simulation."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.services.backtest_engine import run_90_day_backtest

router = APIRouter(prefix="/api", tags=["Backtest & Proof"])


@router.get("/backtest")
def get_backtest_simulation(
    crop: str = Query(..., description="Crop/Commodity name (e.g. Tomato, Onion, Soybean)"),
    district: Optional[str] = Query(None, description="Optional farming origin district (e.g. Pune, Nashik, Latur)"),
    quantity: Optional[float] = Query(20.0, description="Quantity in quintals"),
    vehicle: Optional[str] = Query("tempo", description="Vehicle type: tempo, truck, own_vehicle")
):
    """Simulates trading decisions day-by-day over the historical record (up to 90 days).

    Strictly leak-free: evaluates candidate mandis using only data known before each day,
    and compares realized net earnings against always selling at the nearest local APMC.
    Returns win rate, average extra ₹/quintal, cumulative series, list of worse days,
    and an honest assessment.
    """
    try:
        result = run_90_day_backtest(
            crop=crop,
            district=district,
            quantity_quintals=quantity or 20.0,
            vehicle_type=vehicle or "tempo"
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Backtest simulation failed: {str(exc)}")
