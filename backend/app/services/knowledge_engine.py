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

def search_knowledge(
    project_id: str,
    query: str,
    top_k: int = 5,
    developer_id: str | None = None,
):
    payload = {
        "project_id": project_id,
        "query": query,
        "developer_id": developer_id,
    }

    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/search",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])[:top_k]

def search_assessment_context(
    project_id: str,
    questions: list[dict],
    per_domain: int = 3,
):
    domains = ["APIs", "Architecture", "Database", "Security"]

    contexts = []

    for domain in domains:
        domain_question = next(
            (
                question["question"]
                for question in questions
                if question.get("domain") == domain
            ),
            None,
        )

        if not domain_question:
            continue

        query = f"{domain}: {domain_question}"

        results = search_knowledge(
            project_id=project_id,
            query=query,
            top_k=per_domain,
        )

        for result in results:
            contexts.append({
                "domain": domain,
                "source_file": result.get("source_file", ""),
                "section_title": result.get("section_title", ""),
                "confidence": result.get("confidence", ""),
                "score": result.get("score", 0),
                "context": result.get("context", ""),
            })

    return contexts
def apply_assessment_to_twin(
    developer_id: str,
    project_id: str,
    evaluation: dict,
):
    domain_scores = evaluation.get("domain_scores", {})

    knowledge_areas = {
        "backend_api": domain_scores.get("APIs"),
        "architecture": domain_scores.get("Architecture"),
        "database": domain_scores.get("Database"),
        "authentication": domain_scores.get("Security"),
    }

    knowledge_areas = {
        key: value
        for key, value in knowledge_areas.items()
        if value is not None
    }

    payload = {
        "developer_id": developer_id,
        "project_id": project_id,
        "evaluation": {
            "knowledge_areas": knowledge_areas,
        },
    }

    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/developer-twin/apply-evaluation",
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def create_developer_twin(
    developer_id: str,
    project_id: str,
    skills: dict[str, float],
):
    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/developer-twin",
        json={
            "developer_id": developer_id,
            "project_id": project_id,
            "skills": skills,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

def get_developer_twin(
    developer_id: str,
    project_id: str,
):
    response = requests.get(
        f"{KNOWLEDGE_ENGINE_URL}/developer-twin/{developer_id}",
        params={
            "project_id": project_id,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def upload_developer_profile(file_bytes: bytes, filename: str):
    response = requests.post(
        f"{KNOWLEDGE_ENGINE_URL}/developer-profile/upload",
        files={
            "file": (
                filename,
                file_bytes,
            )
        },
        timeout=60,
    )

    response.raise_for_status()
    return response.json()
