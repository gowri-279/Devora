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
from app.ingest_api import IngestRequest, ingest_files
from app.generate_learning_path import LearningPathRequest, generate_learning_path
from app.projects import get_active_project, list_projects
from app.db import get_chunks_collection
from app.gap_tracker import ( check_and_record_gap, list_open_gaps, resolve_gap, )

app = FastAPI(title="DEVORA Knowledge Engine")
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    return {"total_chunks": get_chunks_collection().count_documents({})}


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
            top_score=top_result["score"] 
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
        repo_metadata=req.repo_metadata
    )

@app.get("/gaps") 
def gaps_endpoint(project_id: str | None = None, min_occurrences: int = 1): 
    return { 
        "gaps": list_open_gaps( 
            project_id=project_id, 
            min_occurrences=min_occurrences, 
        ) 
    } 

@app.post("/gaps/{gap_id}/resolve") 
def resolve_gap_endpoint(gap_id: str): 
    resolved = resolve_gap(gap_id) 
    return { 
        "gap_id": gap_id, 
        "resolved": resolved 
    }