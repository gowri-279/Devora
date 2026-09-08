from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.mongodb import get_db


router = APIRouter(
    prefix="/api",
    tags=["Notifications"],
)


class NotificationCreate(BaseModel):
    recipient_id: str
    role: str
    text: str
    question: str | None = None
    gap_id: str | None = None


@router.get("/notifications")
def get_notifications(
    recipient_id: str,
    role: str,
):
    db = get_db()

    notifications = list(
        db.notifications.find(
            {
                "recipient_id": recipient_id,
                "role": role,
            },
            {"_id": 0},
        ).sort("created_at", -1)
    )

    return {
        "notifications": notifications,
    }


@router.post("/notifications")
def create_notification(notification: NotificationCreate):
    db = get_db()

    document = {
        **notification.model_dump(),
        "read": False,
        "created_at": datetime.now(timezone.utc),
    }

    result = db.notifications.insert_one(document)

    return {
        "status": "success",
        "notification_id": str(result.inserted_id),
    }