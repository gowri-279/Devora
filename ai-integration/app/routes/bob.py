from fastapi import APIRouter
from app.models.schemas import GenerateAnswerRequest, GenerateAnswerResponse
from app.services.bob_service import generate_answer

router = APIRouter()


@router.post("/generate-answer", response_model=GenerateAnswerResponse)
def generate_answer_route(request: GenerateAnswerRequest):
    return generate_answer(request)