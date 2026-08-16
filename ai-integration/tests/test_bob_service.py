from app.models.schemas import Context, GenerateAnswerRequest
from app.services.bob_service import build_prompt


def test_build_prompt():
    request = GenerateAnswerRequest(
        question="How does the refund reconciliation process work?",
        project_id="refund-service",
        contexts=[
            Context(
                source_file="README.md",
                section_title="Reconciliation",
                confidence="high",
                score=0.92,
                context="The refund reconciliation process retries failed operations."
            ),
            Context(
                source_file="API.md",
                section_title="Refund API",
                confidence="medium",
                score=0.81,
                context="The refund API exposes refund retry operations."
            )
        ]
    )

    prompt = build_prompt(request)

    assert "refund reconciliation process" in prompt
    assert "README.md" in prompt
    assert "Reconciliation" in prompt
    assert "API.md" in prompt
    assert "refund-service" in prompt