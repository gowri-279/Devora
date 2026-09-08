from datetime import datetime, timezone

from app.database.mongodb import get_projects_collection


def save_project(
    project_id: str,
    repo_metadata: dict,
):
    now = datetime.now(timezone.utc)

    # The parser's `files` list can be extremely large.
    # It is already consumed during the upload/ingestion pipeline,
    # but it does not need to be persisted for learning-path generation.
    persisted_metadata = {
        key: value
        for key, value in repo_metadata.items()
        if key not in {
            "files",
            "source_artifact",
        }
    }

    project = {
        "project_id": project_id,
        "repo_metadata": persisted_metadata,
        "updated_at": now,
    }

    get_projects_collection().update_one(
        {"project_id": project_id},
        {
            "$set": project,
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )

    return get_project(project_id)


def get_project(
    project_id: str,
):
    return get_projects_collection().find_one(
        {"project_id": project_id},
        {"_id": 0},
    )


def get_repo_metadata(
    project_id: str,
):
    project = get_project(project_id)

    if not project:
        return None

    return project.get("repo_metadata")