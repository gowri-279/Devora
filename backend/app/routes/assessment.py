from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.assessment import (
    save_answers,
    get_assessment,
    save_evaluation,
)
from app.services.assessment_definition import ASSESSMENT_QUESTIONS
from app.services.evaluator import EvaluationResult
from app.services.knowledge_engine import (
    search_assessment_context,
    apply_assessment_to_twin,
    create_developer_twin,
    get_developer_twin,
)
from app.services.ai_integration import evaluate_assessment_with_bob
from uuid import uuid4

from app.services.assessment import (
    save_answers,
    get_assessment,
    save_evaluation,
    create_default_assessment,
)

router = APIRouter(
    prefix="/api/assessments",
    tags=["Assessments"],
)


class AssessmentAnswer(BaseModel):
    question_id: str
    answer: str


class AssessmentSubmitRequest(BaseModel):
    developer_id: str
    answers: list[AssessmentAnswer]


@router.post("/{assessment_id}/submit")
def submit_assessment(
    assessment_id: str,
    request: AssessmentSubmitRequest,
):
    assessment = get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found.",
        )

    if assessment["developer_id"] != request.developer_id:
        raise HTTPException(
            status_code=403,
            detail="Developer does not own this assessment.",
        )

    if not request.answers:
        raise HTTPException(
            status_code=400,
            detail="At least one answer is required.",
        )

    answers = [
        {
            "question_id": answer.question_id,
            "answer": answer.answer,
        }
        for answer in request.answers
    ]

    saved = save_answers(
        assessment_id=assessment_id,
        developer_id=request.developer_id,
        answers=answers,
    )

    if saved is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment could not be updated.",
        )
    
    try:
        contexts = search_assessment_context(
            project_id=assessment["project_id"],
            questions=saved["questions"],
        )

        bob_evaluation = evaluate_assessment_with_bob(
            assessment_id=assessment_id,
            developer_id=request.developer_id,
            project_id=assessment["project_id"],
            questions=saved["questions"],
            answers=saved["answers"],
            contexts=contexts,
        )

        evaluation = EvaluationResult.model_validate(bob_evaluation)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Assessment AI evaluation unavailable: {error}",
        ) from error

    analyzed = save_evaluation(
        assessment_id=assessment_id,
        developer_id=request.developer_id,
        evaluation_result=evaluation,
    )

    if analyzed is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment evaluation could not be saved.",
        )

    try:
        existing_twin = get_developer_twin(
        developer_id=request.developer_id,
        project_id=assessment["project_id"],
        )
        if (
            existing_twin.get("status") == "not_found"
            or existing_twin.get("developer_twin") is None
        ):
            create_developer_twin(
                developer_id=request.developer_id,
                project_id=assessment["project_id"],
                skills=analyzed["scores"],
            )
        twin_update = apply_assessment_to_twin(
            developer_id=request.developer_id,
            project_id=assessment["project_id"],
            evaluation=bob_evaluation,
        )
    except Exception as error:
        raise HTTPException(
        status_code=503,
        detail=f"Developer Twin update unavailable: {error}",
    ) from error

    return {
        "assessment_id": analyzed["assessment_id"],
        "status": analyzed["status"],
        "overall_score": analyzed["overall_score"],
        "scores": analyzed["scores"],
        "next_focus": analyzed["next_focus"],
        "summary": analyzed["summary"],
        "evidence": analyzed["evidence"],
        "analyzed_by": analyzed["analyzed_by"],
    }

class AssessmentCreateRequest(BaseModel):
    developer_id: str
    project_id: str


@router.post("")
def start_assessment(request: AssessmentCreateRequest):
    assessment_id = f"assessment-{uuid4().hex[:12]}"

    assessment = create_default_assessment(
        assessment_id=assessment_id,
        developer_id=request.developer_id,
        project_id=request.project_id,
    )

    return {
        "assessment_id": assessment["assessment_id"],
        "status": assessment["status"],
        "project_id": assessment["project_id"],
        "questions": assessment["questions"],
    }