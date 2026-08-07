""" DEVORA Knowledge Engine service. 
Run: uvicorn app.main:app --reload --port 8001 
This service exposes semantic retrieval APIs for the backend and IBM Bob. It uses MongoDB 
Atlas Vector Search and project-aware retrieval. """


from fastapi import FastAPI
from pydantic import BaseModel
from app.search import search
from fastapi.middleware.cors import CORSMiddleware
from app.confidence import get_confidence
from app.ingest_api import IngestRequest, ingest_files
from app.generate_learning_path import LearningPathRequest, generate_learning_path

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
    from pymongo import MongoClient
    from dotenv import load_dotenv
    import os

    load_dotenv()

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DATABASE")]
    collection = db[os.getenv("MONGODB_COLLECTION")]

    return {
        "total_chunks": collection.count_documents({})
    }


@app.post("/search")
def search_endpoint(req: SearchRequest):
    results = search(req.query, project_id=req.project_id)

    enriched = []

    for r in results:
        confidence = get_confidence(r["score"])

        item = { 
            "source_file": r["source_file"], 
            "scope": r["scope"], 
            "score": round(r["score"], 4), 
            "confidence": confidence, 
            "section_title": r["section_title"], 
            "reference": f"{r['source_file']} → {r['section_title']}", 
            "answer_preview": ( 
                r["context"][:180] + 
                ("..." if len(r["context"]) > 180 else "") 
            ), 
            "context": r["context"] 
        }

        if confidence == "low":
            item["warning"] = (
                "I’m not fully sure. The uploaded documentation may not fully cover this question."
            )

        enriched.append(item)

    return {
        "project_id": req.project_id,
        "query": req.query,
        "results": enriched
    }

@app.post("/ingest") 
def ingest_endpoint(req: IngestRequest): 
    return ingest_files(req)

@app.post("/learning-path") 
def learning_path_endpoint(req: LearningPathRequest): 
    return generate_learning_path(req.project_id)