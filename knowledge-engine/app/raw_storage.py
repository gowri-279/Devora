"""
Stores the untouched original text of every uploaded/cloned document —
separate from knowledge_chunks (which only ever holds post-chunking
pieces). This is what lets you:
  - Re-chunk later with better logic without needing the original files again
  - Let an Admin view/download the source doc as originally uploaded
  - Keep team_foundations.md updatable in place (upsert, not duplicate)
"""

from datetime import datetime, timezone
from typing import Optional

from .db import get_raw_documents_collection


def store_raw_document(
    project_id: Optional[str],
    source_file: str,
    scope: str,
    text: str,
) -> None:
    """
    Upserts by (project_id, source_file) for project docs, or by
    (scope="team", source_file) for team docs — so re-uploading
    team_foundations.md UPDATES it in place rather than creating a
    duplicate, matching your "team foundations can only be updated, never
    removed" requirement.
    """
    collection = get_raw_documents_collection()
    now = datetime.now(timezone.utc)

    key = {"source_file": source_file}
    if scope == "team":
        key["scope"] = "team"
    else:
        key["project_id"] = project_id

    collection.update_one(
        key,
        {
            "$set": {
                "source_file": source_file,
                "scope": scope,
                "project_id": project_id,
                "text": text,
                "status": "active",
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def get_raw_document(source_file: str, project_id: Optional[str] = None, scope: Optional[str] = None) -> Optional[dict]:
    key = {"source_file": source_file}
    if scope == "team":
        key["scope"] = "team"
    elif project_id:
        key["project_id"] = project_id
    return get_raw_documents_collection().find_one(key, {"_id": 0})


def list_raw_documents(project_id: Optional[str] = None, include_archived: bool = False) -> list:
    """Used by generate_learning_path.py to know what's actually been ingested for a project."""
    filter_query = {
        "$or": [
            {"project_id": project_id},
            {"scope": "team"},
        ]
    }
    if not include_archived:
        filter_query["status"] = {"$ne": "archived"}
    return list(get_raw_documents_collection().find(filter_query, {"_id": 0, "text": 0}))
