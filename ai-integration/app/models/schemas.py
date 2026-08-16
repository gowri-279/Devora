from pydantic import BaseModel
from typing import List


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