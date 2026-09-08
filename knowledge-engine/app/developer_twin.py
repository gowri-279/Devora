"""
Developer Twin

Stores and manages a developer's estimated technical knowledge
for a specific Devora project.

The initial twin comes from the developer's uploaded skill profile.
Later, IBM Bob assessment results can update the twin.
"""

from datetime import datetime, timezone
from typing import Optional

from app.db import get_developer_twins_collection


def create_or_update_twin(
    developer_id: str,
    project_id: str,
    skills: dict[str, float],
    source: str = "skill_profile",
) -> dict:
    """
    Create a new Developer Twin or update an existing one.

    Skill scores are normalized to the range 0-100.
    """

    normalized_skills = {}

    for skill, score in skills.items():
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            continue

        normalized_skills[skill.strip().lower()] = max(
            0.0,
            min(100.0, numeric_score),
        )

    now = datetime.now(timezone.utc)

    collection = get_developer_twins_collection()

    existing = collection.find_one(
        {
            "developer_id": developer_id,
            "project_id": project_id,
        }
    )

    if existing:
        version = existing.get("version", 1) + 1

        collection.update_one(
            {
                "developer_id": developer_id,
                "project_id": project_id,
            },
            {
                "$set": {
                    "skills": normalized_skills,
                    "source": source,
                    "version": version,
                    "updated_at": now,
                }
            },
        )

    else:
        version = 1

        collection.insert_one(
            {
                "developer_id": developer_id,
                "project_id": project_id,
                "skills": normalized_skills,
                "source": source,
                "version": version,
                "created_at": now,
                "updated_at": now,
            }
        )

    return get_twin(developer_id, project_id)


def get_twin(
    developer_id: str,
    project_id: str,
) -> Optional[dict]:
    """
    Retrieve a developer's twin for a project.
    """

    return get_developer_twins_collection().find_one(
        {
            "developer_id": developer_id,
            "project_id": project_id,
        },
        {
            "_id": 0,
        },
    )


def update_twin_scores(
    developer_id: str,
    project_id: str,
    knowledge_scores: dict[str, float],
) -> Optional[dict]:
    """
    Update existing Developer Twin scores using later assessment
    results produced by the AI evaluation layer.
    """

    twin = get_twin(developer_id, project_id)

    if not twin:
        return None

    current_skills = twin.get("skills", {}).copy()

    for category, score in knowledge_scores.items():
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            continue

        current_skills[category.strip().lower()] = max(
            0.0,
            min(100.0, numeric_score),
        )

    now = datetime.now(timezone.utc)

    get_developer_twins_collection().update_one(
        {
            "developer_id": developer_id,
            "project_id": project_id,
        },
        {
            "$set": {
                "skills": current_skills,
                "source": "assessment",
                "updated_at": now,
            },
            "$inc": {
                "version": 1,
            },
        },
    )

    return get_twin(developer_id, project_id)