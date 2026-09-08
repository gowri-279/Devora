from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from app.database.mongodb import get_db
from app.services.ai_integration import generate_bob_answer

router = APIRouter(
    prefix="/api",
    tags=["Bob"],
)

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> KNOWLEDGE ENGINE URL:", KNOWLEDGE_ENGINE_URL)

class BobRequest(BaseModel):
    question: str
    project_id: str = "devora"
    developer_id: str | None = None


@router.post("/ask-bob")
def ask_bob(request: BobRequest):

    # Step 1: Ask the Knowledge Engine for relevant context
    try:
        response = requests.post(
            f"{KNOWLEDGE_ENGINE_URL}/search",
            json={
                "project_id": request.project_id,
                "query": request.question,
                "developer_id": request.developer_id,
            },
            timeout=10
        )

        response.raise_for_status()

        knowledge_data = response.json()
            # Notify Admin when a knowledge gap becomes reviewable.
        knowledge_gap = knowledge_data.get("knowledge_gap")
        if knowledge_gap:
            developer_ids = knowledge_gap.get("developer_ids", [])

        if len(developer_ids) >= 2:
            db = get_db()

            existing_notification = db.notifications.find_one({
                "recipient_id": "admin-001",
                "role": "admin",
                "gap_id": knowledge_gap.get("gap_id"),
                "text": "New knowledge gap needs review.",
            })

            if not existing_notification:
                db.notifications.insert_one({
                    "recipient_id": "admin-001",
                    "role": "admin",
                    "text": "New knowledge gap needs review.",
                    "question": knowledge_gap.get("query"),
                    "gap_id": knowledge_gap.get("gap_id"),
                    "read": False,
                    "created_at": datetime.now(timezone.utc),
                })

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Engine unavailable: {str(e)}"
        )

    # Step 2: Get the search results
    results = knowledge_data.get("results", [])

    if not results:
        return {
            "question": request.question,
            "answer": "I could not find enough information in the available project documentation.",
            "sources": []
        }

    # Step 3: Keep only the top 3 results
    top_results = results[:3]

    # Step 4: Build the context for IBM Bob
    contexts = []

    for index, result in enumerate(top_results, start=1):

        context = result.get("context", "")

        contexts.append({
            "number": index,
            "source_file": result.get("source_file", ""),
            "section_title": result.get("section_title", ""),
            "confidence": result.get("confidence", ""),
            "score": result.get("score", 0),
            "context": context
        })

    # Step 5: Build the grounded prompt
    prompt_parts = [
        "You are DEVORA, an onboarding assistant.",
        "",
        "Answer the developer's question using ONLY the provided contexts.",
        "If the contexts are incomplete or confidence is low, say so clearly.",
        "",
        f"Question:\n{request.question}",
        "",
        "Contexts:"
    ]

    for item in contexts:
        prompt_parts.append(
            f"""
[{item["number"]}] {item["source_file"]} → {item["section_title"]}
Confidence: {item["confidence"]}
Score: {item["score"]}

{item["context"]}
"""
        )

    grounded_prompt = "\n".join(prompt_parts)

    # Call AI Integration (IBM Bob / mock) for a grounded answer
    try:
        answer = generate_bob_answer(
            question=request.question,
            project_id=request.project_id,
            contexts=contexts,
        )
    except Exception as e:
        # Degrade gracefully — return the grounded context even if Bob is down
        answer = (
            "The Knowledge Engine found relevant context, but the AI answer "
            f"service is currently unavailable: {e}"
        )

    return {
        "question": request.question,
        "contexts": contexts,
        "answer": answer,
    }