from fastapi import APIRouter

from app.models.schemas import (
    GenerateAnswerRequest,
    GenerateAnswerResponse,
    EvaluateAssessmentRequest,
    EvaluateAssessmentResponse,
    GenerateCurriculumRequest,
    GenerateCurriculumResponse,
)

from app.services.bob_service import generate_answer
from app.services.assessment_evaluator import evaluate_assessment
from app.services.curriculum_service import generate_curriculum


router = APIRouter()


# ============================================================
# Existing IBM Bob Q&A endpoint
# ============================================================

@router.post(
    "/generate-answer",
    response_model=GenerateAnswerResponse,
)
def generate_answer_route(
    request: GenerateAnswerRequest,
):
    return generate_answer(request)


# ============================================================
# Existing assessment evaluation endpoint
# ============================================================

@router.post(
    "/evaluate-assessment",
    response_model=EvaluateAssessmentResponse,
)
def evaluate_assessment_route(
    request: EvaluateAssessmentRequest,
):
    return evaluate_assessment(request)


# ============================================================
# Dynamic Learning Path / Curriculum endpoint
# ============================================================

@router.post(
    "/generate-curriculum",
    response_model=GenerateCurriculumResponse,
)
def generate_curriculum_route(
    request: GenerateCurriculumRequest,
):
    return generate_curriculum(request)