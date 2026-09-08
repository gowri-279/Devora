from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(
    prefix="/api",
    tags=["Knowledge Gaps"],
)

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")


@router.get("/gaps")
def get_gaps(
    project_id: str,
    min_occurrences: int = 1,
):
    try:
        response = requests.get(
            f"{KNOWLEDGE_ENGINE_URL}/gaps",
            params={
                "project_id": project_id,
                "min_occurrences": min_occurrences,
            },
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {e}",
        )


@router.post("/gaps/{gap_id}/resolve")
def resolve_gap(gap_id: str):
    try:
        response = requests.post(
            f"{KNOWLEDGE_ENGINE_URL}/gaps/{gap_id}/resolve",
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {e}",
        )
