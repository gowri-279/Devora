"""
DEVORA Knowledge Engine service.
Run: uvicorn app.main:app --reload --port 8001

This service exposes semantic retrieval APIs for the backend and IBM Bob.
It uses MongoDB Atlas Vector Search and project-aware retrieval.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.search import search
from app.confidence import get_confidence
from app.ingest_api import (
    IngestRequest,
    ingest_files,
    router as ingest_router,
)
from app.generate_learning_path import LearningPathRequest, generate_learning_path
from app.projects import get_active_project, list_projects
from app.db import get_chunks_collection
from app.raw_storage import list_raw_document_content
from app.gap_tracker import ( check_and_record_gap, list_open_gaps, resolve_gap, )
from app.developer_twin import (
    create_or_update_twin,
    get_twin,
)
from app.evaluation import apply_evaluation_to_twin
from app.assessment import generate_assessment
from app.module_quiz import (
    generate_module_quiz,
    check_module_quiz,
    get_module_progress,
)
from app.repository_ingest import ingest_repository_artifact


app = FastAPI(title="DEVORA Knowledge Engine")
app.include_router(ingest_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    project_id: str
    query: str
    developer_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    return {"total_chunks": get_chunks_collection().count_documents({})}

@app.get("/documents")
def documents_endpoint(
    project_id: str,
    include_archived: bool = False,
):
    documents = list_raw_document_content(
        project_id=project_id,
        include_archived=include_archived,
    )

    return {
        "project_id": project_id,
        "documents": documents,
    }

@app.get("/projects")
def projects_endpoint(include_archived: bool = True):
    return {"projects": list_projects(include_archived=include_archived)}


@app.get("/projects/active")
def active_project_endpoint():
    active = get_active_project()
    return {"active_project": active}


@app.post("/search")
def search_endpoint(req: SearchRequest):
    results = search(req.query, project_id=req.project_id)

    enriched = []
    for r in results:
        confidence = get_confidence(r["score"])

        item = { 
            "source_file": r["source_file"], 
            "scope": r["scope"], 
            "source_type": "team" if r["scope"] == "team" else "project", 
            "score": round(r["score"], 4), 
            "confidence": confidence, 
            "section_title": r["section_title"], 
            "summary": r["section_title"], 
            "reference": f"{r['source_file']} → {r['section_title']}", 
            "answer_preview": ( 
                r["context"][:180] + 
                ("..." if len(r["context"]) > 180 else "") 
                ), 
            "context": r["context"] 
        }

        if confidence == "low":
            item["warning"] = (
                "I'm not fully sure. The uploaded documentation may not fully cover this question."
            )

        enriched.append(item)

    top_result = enriched[0] if enriched else None 
    knowledge_gap = None 
    if top_result: 
        knowledge_gap = check_and_record_gap(
            query=req.query,
            project_id=req.project_id,
            top_confidence=top_result["confidence"],
            top_score=top_result["score"],
            developer_id=req.developer_id,
        )

    return { 
        "project_id": req.project_id, 
        "query": req.query, 
        "results": enriched, 
        "knowledge_gap": knowledge_gap 
    }


@app.post("/ingest")
def ingest_endpoint(req: IngestRequest):
    return ingest_files(req)


@app.post("/learning-path")
def learning_path_endpoint(req: LearningPathRequest):
    print("\n========== LEARNING PATH DEBUG ==========")
    print("project_id:", req.project_id)
    print("repo_metadata received:", req.repo_metadata is not None)

    if req.repo_metadata:
        print("repo_metadata keys:", list(req.repo_metadata.keys()))
        print("modules count:", len(req.repo_metadata.get("modules", [])))
        print("dependencies count:", len(req.repo_metadata.get("dependencies", [])))
        print("symbols count:", len(req.repo_metadata.get("symbols", [])))
        print("entrypoints count:", len(req.repo_metadata.get("entrypoints", [])))

    print("=========================================\n")

    return generate_learning_path(
        req.project_id,
        repo_metadata=req.repo_metadata,
        developer_id=req.developer_id,
    )

@app.get("/gaps")
def gaps_endpoint(
    project_id: str | None = None,
    min_occurrences: int = 1,
    status: str = "open",
):
    return {
        "gaps": list_open_gaps(
            project_id=project_id,
            min_occurrences=min_occurrences,
            status=status,
        )
    }

@app.post("/gaps/{gap_id}/resolve") 
def resolve_gap_endpoint(gap_id: str): 
    resolved = resolve_gap(gap_id) 
    return { 
        "gap_id": gap_id, 
        "resolved": resolved 
    }

class DeveloperTwinRequest(BaseModel):
    developer_id: str
    project_id: str
    skills: dict[str, float]


@app.post("/developer-twin")
def create_developer_twin(req: DeveloperTwinRequest):
    twin = create_or_update_twin(
        developer_id=req.developer_id,
        project_id=req.project_id,
        skills=req.skills,
    )

    return {
        "status": "success",
        "developer_twin": twin,
    }


class TwinEvaluationRequest(BaseModel):
    developer_id: str
    project_id: str
    evaluation: dict


@app.post("/developer-twin/apply-evaluation")
def apply_developer_twin_evaluation(req: TwinEvaluationRequest):
    return apply_evaluation_to_twin(
        developer_id=req.developer_id,
        project_id=req.project_id,
        evaluation=req.evaluation,
    )


@app.get("/developer-twin/{developer_id}")
def get_developer_twin(
    developer_id: str,
    project_id: str,
):
    twin = get_twin(
        developer_id=developer_id,
        project_id=project_id,
    )

    if not twin:
        return {
            "status": "not_found",
            "developer_twin": None,
        }

    return {
        "status": "success",
        "developer_twin": twin,
    }

class AssessmentRequest(BaseModel):
    project_id: str
    developer_id: str
    repo_metadata: dict | None = None

class ModuleQuizGenerateRequest(BaseModel):
    project_id: str
    module_step: int
    developer_id: str | None = None
    repo_metadata: dict | None = None


class ModuleQuizCheckRequest(BaseModel):
    project_id: str
    module_step: int
    developer_id: str
    answers: list[int]
    repo_metadata: dict | None = None

@app.post("/assessment/generate")
def generate_assessment_endpoint(req: AssessmentRequest):
    return generate_assessment(
        req.project_id,
        req.developer_id,
        repo_metadata=req.repo_metadata,
    )

@app.post("/modules/quiz/generate")
def generate_module_quiz_endpoint(req: ModuleQuizGenerateRequest):
    return generate_module_quiz(
        project_id=req.project_id,
        module_step=req.module_step,
        developer_id=req.developer_id,
        repo_metadata=req.repo_metadata,
    )


@app.post("/modules/quiz/check")
def check_module_quiz_endpoint(req: ModuleQuizCheckRequest):
    return check_module_quiz(
        project_id=req.project_id,
        module_step=req.module_step,
        developer_id=req.developer_id,
        answers=req.answers,
        repo_metadata=req.repo_metadata,
    )


@app.get("/modules/progress")
def get_module_progress_endpoint(
    developer_id: str,
    project_id: str,
):
    return {
        "developer_id": developer_id,
        "project_id": project_id,
        "completed_modules": get_module_progress(
            developer_id=developer_id,
            project_id=project_id,
        ),
    }

class RepositoryIngestRequest(BaseModel):
    project_id: str
    artifact_url: str
    is_new_project: bool = True

@app.post("/modules/progress/complete")
def complete_module_progress_endpoint(
    developer_id: str,
    project_id: str,
    module_step: int,
):
    from app.module_quiz import complete_module_progress

    return complete_module_progress(
        developer_id=developer_id,
        project_id=project_id,
        module_step=module_step,
    )

@app.post("/ingest/repository")
def ingest_repository_endpoint(req: RepositoryIngestRequest):
    return ingest_repository_artifact(
        project_id=req.project_id,
        artifact_url=req.artifact_url,
        is_new_project=req.is_new_project,
    )