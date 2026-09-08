from typing import List

from pydantic import BaseModel, Field


# ============================================================
# Existing IBM Bob Q&A schemas
# ============================================================

class Context(BaseModel):
    source_file: str
    section_title: str
    confidence: str
    score: float
    context: str


class GenerateAnswerRequest(BaseModel):
    question: str
    project_id: str
    contexts: List[Context]


class Reference(BaseModel):
    source_file: str
    section_title: str


class GenerateAnswerResponse(BaseModel):
    answer: str
    confidence: str
    score: float
    references: List[Reference]


# ============================================================
# Existing assessment schemas
# ============================================================

class AssessmentQuestion(BaseModel):
    question_id: str
    domain: str
    question: str


class AssessmentAnswer(BaseModel):
    question_id: str
    answer: str


class EvaluateAssessmentRequest(BaseModel):
    assessment_id: str
    developer_id: str
    project_id: str
    questions: List[AssessmentQuestion]
    answers: List[AssessmentAnswer]
    contexts: List[Context]


class DomainEvaluation(BaseModel):
    score: int
    confidence: str
    evidence: str


class EvaluateAssessmentResponse(BaseModel):
    evaluator: str
    domain_scores: dict[str, DomainEvaluation]
    cross_domain_evidence: List[str]
    overall_score: int
    summary: str
    next_focus: str


# ============================================================
# Learning Path / Curriculum schemas
# ============================================================

class CurriculumSource(BaseModel):
    source_file: str
    section_title: str
    evidence: str


class CurriculumLesson(BaseModel):
    concept: str
    explanation: str
    why_it_matters: str
    how_project_implements_it: str
    repository_exploration: List[str] = Field(default_factory=list)
    key_takeaway: str
    sources: List[CurriculumSource] = Field(default_factory=list)


class CurriculumModule(BaseModel):
    title: str
    description: str
    difficulty: str
    estimated_minutes: int
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    lessons: List[CurriculumLesson] = Field(default_factory=list)


class GenerateCurriculumRequest(BaseModel):
    project_id: str
    repository_summary: dict
    repository_modules: List[dict] = Field(default_factory=list)
    project_evidence: List[dict] = Field(default_factory=list)
    developer_profile: dict | None = None


class GenerateCurriculumResponse(BaseModel):
    project_id: str
    modules: List[CurriculumModule] = Field(default_factory=list)