from fastapi import APIRouter

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard():
    return {
        "message": "Dashboard endpoint is working!"
    }