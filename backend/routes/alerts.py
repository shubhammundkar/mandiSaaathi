"""API routes for alerts, farmer reports, and data quality."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.alerts_service import (
    delete_alert,
    generate_morning_alert_preview,
    get_active_alerts,
    get_data_quality,
    get_farmer_reports,
    save_farmer_report,
    subscribe_alert,
)

router = APIRouter(prefix="/api", tags=["Alerts & Community"])


class SubscribeRequest(BaseModel):
    crop: str = Field(..., description="Crop name (e.g. Tomato, Onion)")
    district: str = Field(..., description="Farmer district (e.g. Pune, Nashik)")
    language: Optional[str] = Field("mr", description="Language: en, hi, mr")
    nickname: Optional[str] = Field("शेतकरी मित्र", description="Farmer name or nickname")


class FarmerReportRequest(BaseModel):
    crop: str = Field(..., description="Crop sold (e.g. Tomato, Onion)")
    market: str = Field(..., description="Mandi/market where sold (e.g. Pune, Pimpalgaon)")
    price: float = Field(..., gt=0, le=50000, description="Selling price per quintal in ₹")
    quantity: float = Field(..., gt=0, le=10000, description="Quantity sold in quintals")
    report_date: Optional[str] = Field(None, description="Date of sale (YYYY-MM-DD)")


# -----------------------------------------------------------------------------
# 1. Alert Subscriptions & WhatsApp Preview
# -----------------------------------------------------------------------------

@router.post("/alerts/subscribe")
def api_subscribe_alert(payload: SubscribeRequest):
    """Subscribes a farmer to daily price alerts."""
    try:
        res = subscribe_alert(
            crop=payload.crop,
            district=payload.district,
            language=payload.language or "mr",
            nickname=payload.nickname
        )
        return res
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(exc)}")


@router.get("/alerts")
def api_list_alerts():
    """Lists all active alert subscriptions."""
    try:
        return {"subscriptions": get_active_alerts()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(exc)}")


@router.delete("/alerts/{subscription_id}")
def api_delete_alert(subscription_id: int):
    """Unsubscribes / deactivates an alert subscription."""
    try:
        success = delete_alert(subscription_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert subscription not found.")
        return {"status": "success", "message": "Subscription cancelled."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(exc)}")


@router.get("/alerts/preview")
@router.post("/alerts/preview")
def api_alert_preview(
    crop: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    language: Optional[str] = Query("mr"),
    nickname: Optional[str] = Query(None),
    payload: Optional[SubscribeRequest] = None
):
    """Generates a WhatsApp-style morning message preview using real advisory data."""
    try:
        c = (payload.crop if payload else None) or crop or "Tomato"
        d = (payload.district if payload else None) or district or "Pune"
        l = (payload.language if payload else None) or language or "mr"
        n = (payload.nickname if payload else None) or nickname or "शेतकरी मित्र"

        preview = generate_morning_alert_preview(
            crop=c,
            district=d,
            language=l,
            nickname=n
        )
        return preview
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(exc)}")


# -----------------------------------------------------------------------------
# 2. "I sold today" Farmer Reports
# -----------------------------------------------------------------------------

@router.post("/farmer-reports")
def api_submit_farmer_report(payload: FarmerReportRequest):
    """Submits a crowd-sourced transaction to farmer_reports with strict sanity checks.
    
    Shown separately with 'Farmer reported' badge, never mixed into Agmarknet figures.
    """
    try:
        res = save_farmer_report(
            crop=payload.crop,
            market=payload.market,
            price=payload.price,
            quantity=payload.quantity,
            report_date=payload.report_date
        )
        return res
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save farmer report: {str(exc)}")


@router.get("/farmer-reports")
def api_list_farmer_reports(
    crop: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """Lists crowd-sourced farmer reports. Always returned with 'Farmer reported' badge."""
    try:
        reports = get_farmer_reports(crop=crop, market=market, limit=limit)
        return {
            "source": "farmer_reported",
            "badge": "Farmer reported",
            "total_reports": len(reports),
            "reports": reports
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch farmer reports: {str(exc)}")


# -----------------------------------------------------------------------------
# 3. Data Quality & Coverage
# -----------------------------------------------------------------------------

@router.get("/data-quality")
def api_data_quality():
    """Returns data quality metrics per mandi: last reported date, 30-day coverage, and confidence badge."""
    try:
        return get_data_quality()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to calculate data quality: {str(exc)}")
