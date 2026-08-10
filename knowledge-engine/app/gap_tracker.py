"""
Knowledge Gap Loop — now with SEMANTIC dedup.

Every time /search runs, main.py calls check_and_record_gap() with the
top result's confidence. If it's "low" (or there were no results at
all), we log it here.

Dedup now works by embedding the query and comparing it (cosine
similarity) against the embeddings of currently-open gaps for the same
project. Above SIMILARITY_THRESHOLD, it's treated as the same underlying
question and occurrence_count increments; below it, a new gap is created.

This replaces the old exact-string-normalization dedup, which missed
paraphrases like "how does auth work" vs "explain the login flow."

Tuning note: SIMILARITY_THRESHOLD is the one knob that matters here. 0.87
is a reasonable starting point for all-MiniLM-L6-v2, but the right value
depends on your actual doc questions — too low merges genuinely different
questions into one gap, too high barely improves on exact-string matching.
If you have time, test it against a handful of real paraphrase pairs from
your own demo questions before the hackathon and adjust.
"""

import uuid
import numpy as np
from datetime import datetime, timezone
from typing import Optional

from .db import get_gaps_collection
from .embeddings import embed_query

SIMILARITY_THRESHOLD = 0.87


def _cosine_similarity(a, b) -> float:
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _find_matching_gap(query_embedding, project_id: str) -> Optional[dict]:
    """
    Brute-force compares against every currently-open gap for this
    project. Fine at hackathon scale (dozens/hundreds of open gaps).
    If this needs to scale later, the natural upgrade is running this as
    an actual $vectorSearch against a vector index on the gaps
    collection, same pattern as chunks — not needed yet.
    """
    collection = get_gaps_collection()
    open_gaps = list(collection.find(
        {"status": "open", "project_id": project_id},
        {"_id": 0, "gap_id": 1, "embedding": 1, "occurrence_count": 1},
    ))

    best_match = None
    best_score = 0.0

    for gap in open_gaps:
        if "embedding" not in gap:
            continue  # older gap records created before this field existed
        score = _cosine_similarity(query_embedding, gap["embedding"])
        if score > best_score:
            best_score = score
            best_match = gap

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        return best_match
    return None


def check_and_record_gap(
    query: str,
    project_id: str,
    top_confidence: str,
    top_score: float,
    developer_id: Optional[str] = None,
) -> Optional[dict]:
    """
    Call this right after /search returns. top_confidence should be
    "high" | "medium" | "low" (from confidence.get_confidence()).

    Returns None if the result was confident enough (no gap). Returns the
    gap record (dict) if this query is/was a knowledge gap — semantically
    matched against existing open gaps for the same project, not just
    exact string matches.
    """
    if top_confidence != "low":
        return None

    query_embedding = embed_query(query)
    collection = get_gaps_collection()
    now = datetime.now(timezone.utc)

    match = _find_matching_gap(query_embedding, project_id)

    if match:
        collection.update_one(
            {"gap_id": match["gap_id"]},
            {
                "$inc": {"occurrence_count": 1},
                "$set": {"last_seen_at": now, "top_score": top_score},
                "$push": {"example_queries": query},  # keeps a few paraphrase examples for Admin to read
            },
        )
        updated = collection.find_one({"gap_id": match["gap_id"]}, {"_id": 0})
        return updated

    gap = {
        "gap_id": uuid.uuid4().hex[:16],
        "query": query,  # the original phrasing that first created this gap
        "example_queries": [query],
        "embedding": query_embedding,
        "project_id": project_id,
        "top_score": top_score,
        "asked_by_developer_id": developer_id,
        "status": "open",
        "occurrence_count": 1,
        "first_seen_at": now,
        "last_seen_at": now,
    }
    collection.insert_one(gap)
    gap.pop("_id", None)
    gap.pop("embedding", None)  # don't send the raw vector back over the API
    return gap


def list_open_gaps(project_id: Optional[str] = None, min_occurrences: int = 1) -> list:
    filter_query = {"status": "open", "occurrence_count": {"$gte": min_occurrences}}
    if project_id:
        filter_query["project_id"] = project_id

    results = list(
        get_gaps_collection()
        .find(filter_query, {"_id": 0, "embedding": 0})  # never leak raw vectors to the API
        .sort("occurrence_count", -1)
    )
    return results


def resolve_gap(gap_id: str) -> bool:
    """Call once Admin updates the relevant doc and it's been re-ingested."""
    result = get_gaps_collection().update_one(
        {"gap_id": gap_id},
        {"$set": {"status": "resolved", "resolved_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count > 0
