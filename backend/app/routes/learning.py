from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os

router = APIRouter(tags=["Learning Path"])

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> KNOWLEDGE ENGINE URL:", KNOWLEDGE_ENGINE_URL)


class LearningPathRequest(BaseModel):
    project_id: str
    repo_metadata: Optional[dict] = None


@router.post("/learning-path")
def get_learning_path(request: LearningPathRequest):

    try:
        url = f"{KNOWLEDGE_ENGINE_URL}/learning-path"
        print(">>> CALLING KE:", url)
        
        response = requests.post(
        url,
        json={
            "project_id": request.project_id,
            "repo_metadata": request.repo_metadata
        },
        timeout=30
    )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {str(e)}"
        )