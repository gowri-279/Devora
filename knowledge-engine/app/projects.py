"""
Multi-project archiving/versioning.

Model (matches what you described): at any time there's exactly one
ACTIVE project per team. When a new repo is cloned / a new project
starts, the previous one gets ARCHIVED — not deleted. Archived data stays
queryable for audit purposes but is excluded from normal search results.

Team-scope docs (project_id=None, e.g. team_foundations.md) are NEVER
archived by this — they persist across every project switch, and are
only ever replaced/updated in place (see raw_storage.py).
"""

from datetime import datetime, timezone
from typing import Optional

from .db import get_projects_collection, get_chunks_collection, get_raw_documents_collection


def get_active_project() -> Optional[dict]:
    return get_projects_collection().find_one({"status": "active"}, {"_id": 0})


def list_projects(include_archived: bool = True) -> list:
    filter_query = {} if include_archived else {"status": "active"}
    return list(get_projects_collection().find(filter_query, {"_id": 0}))


def archive_project(project_id: str) -> None:
    """
    Marks a project's chunks + raw documents as archived (status field),
    and updates its projects_meta record. Does NOT delete anything —
    archived data is still in Mongo, just excluded from default search.
    """
    now = datetime.now(timezone.utc)

    get_chunks_collection().update_many(
        {"project_id": project_id},
        {"$set": {"status": "archived"}},
    )
    get_raw_documents_collection().update_many(
        {"project_id": project_id},
        {"$set": {"status": "archived"}},
    )
    get_projects_collection().update_one(
        {"project_id": project_id},
        {"$set": {"status": "archived", "archived_at": now}},
    )


def start_new_project(project_id: str) -> dict:
    """
    Call this BEFORE ingesting a new project's documents. Archives
    whatever project is currently active (if any, and if it isn't this
    same project_id being re-ingested), then marks/creates this project
    as active.

    Returns the projects_meta record for the now-active project.
    """
    now = datetime.now(timezone.utc)
    projects = get_projects_collection()

    currently_active = get_active_project()
    if currently_active and currently_active["project_id"] != project_id:
        archive_project(currently_active["project_id"])

    projects.update_one(
        {"project_id": project_id},
        {
            "$set": {"status": "active"},
            "$setOnInsert": {"project_id": project_id, "created_at": now},
        },
        upsert=True,
    )

    return projects.find_one({"project_id": project_id}, {"_id": 0})
