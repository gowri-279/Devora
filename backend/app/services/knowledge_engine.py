import os
import requests
from dotenv import load_dotenv

load_dotenv()


KNOWLEDGE_ENGINE_URL = os.getenv(
    "KNOWLEDGE_ENGINE_URL",
    "http://127.0.0.1:8001"
)


def ingest_documents(
    project_id: str,
    file_paths: list[str],
    is_new_project: bool
):
    payload = {
        "project_id": project_id,
        "file_paths": file_paths,
        "is_new_project": is_new_project
    }

    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/ingest",
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()