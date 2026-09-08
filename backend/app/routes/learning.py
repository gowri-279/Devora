from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import requests

from app.services.project import get_repo_metadata

router = APIRouter(
    prefix="/api",
    tags=["Learning Path"],
)

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> KNOWLEDGE ENGINE URL:", KNOWLEDGE_ENGINE_URL)


class LearningPathRequest(BaseModel):
    project_id: str
    developer_id: Optional[str] = None
    repo_metadata: Optional[dict] = None


@router.post("/learning-path")
def get_learning_path(
    request: LearningPathRequest,
):
    try:
        repo_metadata = request.repo_metadata

        if not repo_metadata:
            repo_metadata = get_repo_metadata(
                request.project_id
            )

        if not repo_metadata:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Repository metadata was not found "
                    f"for project '{request.project_id}'. "
                    "Please upload the repository first."
                ),
            )

        url = f"{KNOWLEDGE_ENGINE_URL}/learning-path"

        print(
            ">>> CALLING KE:",
            url,
        )

        response = requests.post(
            url,
            json={
                "project_id": request.project_id,
                "repo_metadata": repo_metadata,
                "developer_id": request.developer_id,
            },
            timeout=300,
        )

        response.raise_for_status()

        return response.json()

    except HTTPException:
        raise

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Knowledge Engine unavailable: "
                f"{str(e)}"
            ),
        )