from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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