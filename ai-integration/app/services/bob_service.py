from app.models.schemas import GenerateAnswerRequest, GenerateAnswerResponse


def generate_answer(request: GenerateAnswerRequest) -> GenerateAnswerResponse:
    return GenerateAnswerResponse(
        answer="Mock Bob response: I received the question and contexts.",
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