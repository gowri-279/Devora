import os

import requests
from dotenv import load_dotenv

load_dotenv()

AI_INTEGRATION_URL = os.getenv(
    "AI_INTEGRATION_URL",
    "http://127.0.0.1:8002",
)


def evaluate_assessment_with_bob(
    assessment_id: str,
    developer_id: str,
    project_id: str,
    questions: list[dict],
    answers: list[dict],
    contexts: list[dict],
):
    payload = {
        "assessment_id": assessment_id,
        "developer_id": developer_id,
        "project_id": project_id,
        "questions": questions,
        "answers": answers,
        "contexts": contexts,
    }

    try:
        response = requests.post(
            f"{AI_INTEGRATION_URL}/evaluate-assessment",
            json=payload,
            timeout=150,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"AI Integration unavailable: {error}"
        ) from error

    return response.json()


def generate_bob_answer(
    question: str,
    project_id: str,
    contexts: list[dict],
) -> str:
    """
    Call AI Integration /generate-answer and return Bob's answer string.
    """
    payload = {
        "question": question,
        "project_id": project_id,
        "contexts": [
            {
                "source_file": c.get("source_file", ""),
                "section_title": c.get("section_title", ""),
                "confidence": c.get("confidence", "medium"),
                "score": c.get("score", 0.0),
                "context": c.get("context", ""),
            }
            for c in contexts
        ],
    }

    try:
        response = requests.post(
            f"{AI_INTEGRATION_URL}/generate-answer",
            json=payload,
            timeout=150,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"AI Integration unavailable: {error}"
        ) from error

    data = response.json()
    return data.get("answer", "No answer returned by AI Integration.")
