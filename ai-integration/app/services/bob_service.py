from app.models.schemas import GenerateAnswerRequest, GenerateAnswerResponse
from app.services.ibm_bob_client import IBMBobClient


def generate_answer(request: GenerateAnswerRequest) -> GenerateAnswerResponse:
    if not request.contexts:
        raise ValueError(
            "No grounded contexts were provided by the Knowledge Engine."
        )

    client = IBMBobClient()

    prompt = build_prompt(request)

    answer = client.generate(prompt)

    return GenerateAnswerResponse(
        answer=answer,
        confidence=request.contexts[0].confidence,
        score=request.contexts[0].score,
        references=[
            {
                "source_file": context.source_file,
                "section_title": context.section_title
            }
            for context in request.contexts
        ]
    )


def build_prompt(request: GenerateAnswerRequest) -> str:
    contexts = "\n\n".join(
        f"Source: {context.source_file}\n"
        f"Section: {context.section_title}\n"
        f"Context: {context.context}"
        for context in request.contexts
    )

    return f"""
You are DEVORA, an AI onboarding assistant for software developers.

Answer the developer's question using ONLY the provided project context.
Do not invent information that is not present in the context.

Project:
{request.project_id}

Developer question:
{request.question}

Retrieved project context:
{contexts}

Give a clear, concise answer suitable for a developer.
""".strip()