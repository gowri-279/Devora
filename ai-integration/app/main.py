from fastapi import FastAPI
from app.routes.bob import router as bob_router

app = FastAPI(title="Devora AI Integration")

app.include_router(bob_router)


@app.get("/")
def root():
    return {
        "message": "Devora AI Integration is running"
    }