import json

from app.models.schemas import (
    EvaluateAssessmentRequest,
    EvaluateAssessmentResponse,
)
from app.services.assessment_prompt import build_assessment_prompt
from app.services.ibm_bob_client import IBMBobClient


def _parse_bob_json(response: str) -> dict:
    """
    Parse JSON returned by IBM Bob.

    Bob is instructed to return JSON only, but this also handles
    accidental Markdown code fences.
    """
    cleaned = response.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].lstrip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "IBM Bob returned a response that was not valid JSON."
        ) from error

    if not isinstance(parsed, dict):
        raise RuntimeError(
            "IBM Bob returned JSON, but the result was not an object."
        )

    return parsed


def evaluate_assessment(
    request: EvaluateAssessmentRequest,
) -> EvaluateAssessmentResponse:
    prompt = build_assessment_prompt(request)

    client = IBMBobClient()
    raw_response = client.generate(prompt)

    data = _parse_bob_json(raw_response)

    try:
        return EvaluateAssessmentResponse.model_validate(data)
    except Exception as error:
        raise RuntimeError(
            "IBM Bob returned an invalid assessment evaluation structure."
        ) from error