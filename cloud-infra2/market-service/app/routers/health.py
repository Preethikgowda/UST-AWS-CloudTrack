"""
IntelliWealth - Market Service Health Endpoints
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service health check")
async def health_check():
    return {"status": "ok"}


@router.get("/readiness", summary="Readiness probe")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "db": "ok"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "db": "error"},
        )


@router.get("/liveness", summary="Liveness probe")
async def liveness_check():
    return {"status": "alive"}
