from datetime import datetime, timezone

from app.database.mongodb import get_assessments_collection
from app.services.assessment_definition import ASSESSMENT_QUESTIONS


def create_assessment(
    assessment_id: str,
    developer_id: str,
    project_id: str,
    questions: list[dict],
):
    now = datetime.now(timezone.utc)

    assessment = {
        "assessment_id": assessment_id,
        "developer_id": developer_id,
        "project_id": project_id,
        "questions": questions,
        "answers": [],
        "status": "pending",
        "overall_score": None,
        "scores": {},
        "strengths": [],
        "knowledge_gaps": [],
        "summary": None,
        "evidence": [],
        "analyzed_by": None,
        "created_at": now,
        "updated_at": now,
    }

    get_assessments_collection().update_one(
        {"assessment_id": assessment_id},
        {"$setOnInsert": assessment},
        upsert=True,
    )

    return get_assessment(assessment_id)


def get_assessment(assessment_id: str):
    return get_assessments_collection().find_one(
        {"assessment_id": assessment_id},
        {"_id": 0},
    )

def create_default_assessment(
    assessment_id: str,
    developer_id: str,
    project_id: str,
):
    return create_assessment(
        assessment_id=assessment_id,
        developer_id=developer_id,
        project_id=project_id,
        questions=ASSESSMENT_QUESTIONS,
    )

def save_answers(
    assessment_id: str,
    developer_id: str,
    answers: list[dict],
):
    now = datetime.now(timezone.utc)

    result = get_assessments_collection().update_one(
        {
            "assessment_id": assessment_id,
            "developer_id": developer_id,
        },
        {
            "$set": {
                "answers": answers,
                "status": "submitted",
                "updated_at": now,
            }
        },
    )

    if result.matched_count == 0:
        return None

    return get_assessment(assessment_id)

def save_evaluation(
    assessment_id: str,
    developer_id: str,
    evaluation_result,
):
    now = datetime.now(timezone.utc)

    scores = {
        domain: evaluation.score
        for domain, evaluation in evaluation_result.domain_scores.items()
    }

    evidence = [
        {
            "domain": domain,
            "score": evaluation.score,
            "confidence": evaluation.confidence,
            "reason": evaluation.evidence,
        }
        for domain, evaluation in evaluation_result.domain_scores.items()
    ]

    evidence.extend(
        {
            "type": "cross_domain",
            "reason": item,
        }
        for item in evaluation_result.cross_domain_evidence
    )

    result = get_assessments_collection().update_one(
        {
            "assessment_id": assessment_id,
            "developer_id": developer_id,
        },
        {
            "$set": {
                "status": "analyzed",
                "overall_score": evaluation_result.overall_score,
                "scores": scores,
                "summary": evaluation_result.summary,
                "next_focus": evaluation_result.next_focus,
                "evidence": evidence,
                "analyzed_by": evaluation_result.evaluator,
                "updated_at": now,
            }
        },
    )

    if result.matched_count == 0:
        return None

    return get_assessment(assessment_id)