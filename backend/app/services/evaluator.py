from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


Domain = Literal["APIs", "Architecture", "Database", "Security"]


class DomainEvaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    evidence: str


class EvaluationResult(BaseModel):
    evaluator: Literal["mock", "ibm_bob"]

    domain_scores: dict[Domain, DomainEvaluation]

    cross_domain_evidence: list[str] = Field(default_factory=list)

    overall_score: int = Field(ge=0, le=100)
    summary: str
    next_focus: Domain

class AssessmentEvaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        questions: list[dict],
        answers: list[dict],
    ) -> EvaluationResult:
        pass