from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


@router.get("/health", response_model=HealthResponse)
def get_health():
    # Database status will be dynamically verified in Module 3
    return HealthResponse(
        status="ok",
        version="1.0.0",
        database="connected"
    )
