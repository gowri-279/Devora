from fastapi import APIRouter, HTTPException

from app.services.knowledge_engine import get_developer_twin


router = APIRouter(
    prefix="/api",
    tags=["Developer Twin"],
)


@router.get("/developer-twin/{developer_id}")
def get_twin(
    developer_id: str,
    project_id: str,
):
    try:
        return get_developer_twin(
            developer_id=developer_id,
            project_id=project_id,
        )

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Developer Twin unavailable: {error}",
        ) from error