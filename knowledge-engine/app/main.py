""" DEVORA Knowledge Engine service. 
Run: uvicorn app.main:app --reload --port 8001 
This service exposes semantic retrieval APIs for the backend and IBM Bob. It uses MongoDB 
Atlas Vector Search and project-aware retrieval. """


from fastapi import FastAPI
from pydantic import BaseModel
from app.search import search
from fastapi.middleware.cors import CORSMiddleware
from app.confidence import get_confidence

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