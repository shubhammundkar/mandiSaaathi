from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import FRONTEND_DIR
from backend.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()
    yield

app = FastAPI(
    title="Mandi Saathi API",
    description="AI Mandi Price and Sell-Timing Advisor for Indian Farmers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "Mandi Saathi",
        "version": "1.0.0",
        "hackathon": "VORTEX 2K26"
    }

from backend.routes.crops import router as crops_router
from backend.routes.advisor import router as advisor_router
from backend.routes.forecast import router as forecast_router
from backend.routes.backtest import router as backtest_router

# Include API Routers
app.include_router(crops_router)
app.include_router(advisor_router)
app.include_router(forecast_router)
app.include_router(backtest_router)

# Mount static files for frontend at root
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
