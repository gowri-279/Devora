from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.learning import router as learning_router
from app.routes.upload import router as upload_router
from app.routes.notifications import router as notifications_router
from app.routes.analytics import router as analytics_router
from app.routes.bob import router as bob_router

app = FastAPI(
    title="Devora Backend API",
    description="Backend API for the Devora AI Developer Onboarding Platform",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(learning_router)
app.include_router(upload_router)
app.include_router(notifications_router)
app.include_router(analytics_router)
app.include_router(bob_router)

@app.get("/")
def home():
    return {
        "project": "Devora",
        "status": "Running 🚀",
        "message": "Welcome to the Devora Backend!"
    }