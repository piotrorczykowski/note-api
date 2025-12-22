from fastapi import APIRouter
from app.schemas.health import HealthDto

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Check API Health",
    response_description="API status",
    response_model=HealthDto,
)
def healthcheck() -> HealthDto:
    return {"status": "ok"}
