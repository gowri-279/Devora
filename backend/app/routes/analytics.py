from fastapi import APIRouter

router = APIRouter(tags=["Analytics"])


@router.get("/analytics")
def get_analytics():
    return {
        "analytics": {}
    }