from fastapi import APIRouter

router = APIRouter(tags=["Notifications"])


@router.get("/notifications")
def get_notifications():
    return {
        "notifications": []
    }