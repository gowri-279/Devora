from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter(tags=["Bob"])

KNOWLEDGE_ENGINE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> KNOWLEDGE ENGINE URL:", KNOWLEDGE_ENGINE_URL)

class BobRequest(BaseModel):
    question: str
    project_id: str = "devora"


@router.post("/ask-bob")
def ask_bob(request: BobRequest):

    # Step 1: Ask the Knowledge Engine for relevant context
    try:
        response = requests.post(
            f"{KNOWLEDGE_ENGINE_URL}/search",
            json={
                "project_id": request.project_id,
                "query": request.question
            },
            timeout=10
        )

        response.raise_for_status()

        knowledge_data = response.json()

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

    # Temporary response until IBM Bob integration is connected
    return {
        "question": request.question,
        "prompt": grounded_prompt,
        "contexts": contexts,
        "answer": "Knowledge Engine context retrieved successfully. IBM Bob integration is pending."
    }