import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


AI_INTEGRATION_URL = os.getenv(
    "DEVORA_AI_INTEGRATION_URL",
    "http://localhost:8002",
)


def generate_curriculum(
    project_id: str,
    repository_summary: dict,
    repository_modules: list,
    project_evidence: list,
    developer_profile: dict | None = None,
) -> dict:

    payload = {
        "project_id": project_id,
        "repository_summary": repository_summary,
        "repository_modules": repository_modules,
        "project_evidence": project_evidence,
        "developer_profile": developer_profile or {},
    }

    body = json.dumps(payload, default=str).encode("utf-8")

    request = Request(
        f"{AI_INTEGRATION_URL.rstrip('/')}/generate-curriculum",
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            response_body = response.read().decode(
                "utf-8"
            )

    except HTTPError as error:
        message = error.read().decode(
            "utf-8",
            errors="replace",
        )
        raise RuntimeError(
            f"AI curriculum generation failed "
            f"({error.code}): {message}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            "Could not connect to DEVORA AI Integration. "
            f"Expected service at {AI_INTEGRATION_URL}"
        ) from error

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "AI Integration returned invalid JSON."
        ) from error