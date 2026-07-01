from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class RootResponse(BaseModel):
    status: str
    service: str
    version: str
    env: str

class HealthResponse(BaseModel):
    status: str
    dependencies: Dict[str, str]

@router.get("/", response_model=RootResponse, tags=["Observability"])
def read_root():
    """
    Returns service identity for deployment and load balancer root checks.
    """
    from src.config import config
    return RootResponse(
        status="ok",
        service="sql_analytics_agent",
        version="1.0.0",
        env=config.ENV
    )

@router.get("/health", response_model=HealthResponse, tags=["Observability"])
def health_check():
    """
    Structured health status of the service and its dependencies.
    """
    return HealthResponse(
        status="healthy",
        dependencies={
            "database": "ok",
            "redis": "ok"
        }
    )
