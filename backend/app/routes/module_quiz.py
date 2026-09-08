from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os


router = APIRouter(tags=["Module Quiz"])

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> KNOWLEDGE ENGINE URL:", KNOWLEDGE_ENGINE_URL)


class ModuleQuizGenerateRequest(BaseModel):
    project_id: str
    module_step: int
    developer_id: Optional[str] = None
    repo_metadata: Optional[dict] = None


class ModuleQuizCheckRequest(BaseModel):
    project_id: str
    module_step: int
    developer_id: str
    answers: list[int]
    repo_metadata: Optional[dict] = None


@router.post("/modules/quiz/generate")
def generate_module_quiz(request: ModuleQuizGenerateRequest):

    try:
        response = requests.post(
            f"{KNOWLEDGE_ENGINE_URL}/modules/quiz/generate",
            json={
                "project_id": request.project_id,
                "module_step": request.module_step,
                "developer_id": request.developer_id,
                "repo_metadata": request.repo_metadata,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {str(e)}"
        )


@router.post("/modules/quiz/check")
def check_module_quiz(request: ModuleQuizCheckRequest):

    try:
        response = requests.post(
            f"{KNOWLEDGE_ENGINE_URL}/modules/quiz/check",
            json={
                "project_id": request.project_id,
                "module_step": request.module_step,
                "developer_id": request.developer_id,
                "answers": request.answers,
                "repo_metadata": request.repo_metadata,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {str(e)}"
        )


@router.get("/modules/progress")
def get_module_progress(
    developer_id: str,
    project_id: str,
):

    try:
        response = requests.get(
            f"{KNOWLEDGE_ENGINE_URL}/modules/progress",
            params={
                "developer_id": developer_id,
                "project_id": project_id,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {str(e)}"
        )

@router.post("/modules/progress/complete")
def complete_module_progress(
    developer_id: str,
    project_id: str,
    module_step: int,
):
    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/modules/progress/complete",
        params={
            "developer_id": developer_id,
            "project_id": project_id,
            "module_step": module_step,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    return response.json()