"""
Stores the untouched original text of every uploaded/cloned document.

raw_documents is separate from knowledge_chunks:

    raw_documents
        = complete original document

    knowledge_chunks
        = processed/chunked content used for retrieval

The raw document store is also the source for the
repository-grounded learning-path course-content layer.

Team documents are shared across projects and are never
archived when a project changes.

Project documents are associated with a specific project and
can be archived when that project is no longer active.
"""

from datetime import datetime, timezone
from typing import Optional

from .db import get_raw_documents_collection


# ============================================================
# STORE
# ============================================================

def store_raw_document(
    project_id: Optional[str],
    source_file: str,
    scope: str,
    text: str,
) -> None:
    """
    Upsert the untouched original document.

    Project documents are keyed by:

        (project_id, source_file)

    Team documents are keyed by:

        (scope="team", source_file)

    Re-uploading the same document therefore updates the
    existing record instead of creating duplicates.
    """

    collection = get_raw_documents_collection()

    now = datetime.now(timezone.utc)

    key = {
        "source_file": source_file,
    }

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
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )


# ============================================================
# SINGLE DOCUMENT
# ============================================================

def get_raw_document(
    source_file: str,
    project_id: Optional[str] = None,
    scope: Optional[str] = None,
) -> Optional[dict]:
    """
    Retrieve one raw document.

    Used when the course-content layer needs the complete
    original source text.
    """

    key = {
        "source_file": source_file,
    }

    if scope == "team":
        key["scope"] = "team"

    elif project_id is not None:
        key["project_id"] = project_id

    return get_raw_documents_collection().find_one(
        key,
        {
            "_id": 0,
        },
    )


# ============================================================
# LIGHTWEIGHT DOCUMENT LIST
# ============================================================

def list_raw_documents(
    project_id: Optional[str] = None,
    include_archived: bool = False,
) -> list:
    """
    Return raw-document metadata without the full text.

    Team documents are always included because they are shared
    across projects.

    By default:

        - active project documents are included
        - active team documents are included
        - archived project documents are excluded
    """

    filter_query = {
        "$or": [
            {
                "project_id": project_id,
            },
            {
                "scope": "team",
            },
        ]
    }

    if not include_archived:
        filter_query["status"] = {
            "$ne": "archived",
        }

    return list(
        get_raw_documents_collection().find(
            filter_query,
            {
                "_id": 0,
                "text": 0,
            },
        )
    )


# ============================================================
# FULL DOCUMENT CONTENT
# ============================================================

def list_raw_document_content(
    project_id: Optional[str] = None,
    include_archived: bool = False,
) -> list:
    """
    Return complete raw documents for a project.

    Includes:

        - active project documents
        - shared team documents

    Archived project documents are excluded by default.

    The original text is preserved exactly as stored.
    """

    filter_query = {
        "$or": [
            {
                "project_id": project_id,
            },
            {
                "scope": "team",
            },
        ]
    }

    if not include_archived:
        filter_query["status"] = {
            "$ne": "archived",
        }

    return list(
        get_raw_documents_collection().find(
            filter_query,
            {
                "_id": 0,
            },
        ).sort(
            "source_file",
            1,
        )
    )


# ============================================================
# SOURCE-PATH MATCHING
# ============================================================

def get_documents_for_module(
    module_path: str,
    project_id: Optional[str] = None,
) -> list:
    """
    Return complete raw documents belonging to a repository
    learning module.

    Matching is based on the DIRECTORY containing the source
    file, not recursive prefix matching.

    Example:

        module_path:
            fastapi/security

        matches:

            fastapi/security/__init__.py
            fastapi/security/api_key.py
            fastapi/security/base.py
            fastapi/security/http.py
            fastapi/security/oauth2.py

        does NOT match:

            fastapi/security/oauth2/something.py
            fastapi/openapi/utils.py
            fastapi/middleware/cors.py

    For the root package:

        fastapi

    files directly under:

        fastapi/

    are included.
    """

    module_path = (
        module_path
        .replace("\\", "/")
        .strip("/")
    )

    documents = list_raw_document_content(
        project_id=project_id,
        include_archived=False,
    )

    matched = []

    for document in documents:

        source_file = (
            document.get(
                "source_file",
                "",
            )
            .replace("\\", "/")
            .strip("/")
        )

        if not source_file:
            continue

        # Exact source-file match.
        if source_file == module_path:
            matched.append(document)
            continue

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Match only files whose immediate parent directory
        # is the requested module.
        #
        # This prevents a module from recursively swallowing
        # nested submodules.
        # ----------------------------------------------------

        source_parts = source_file.split("/")
        module_parts = module_path.split("/")

        if len(source_parts) != len(module_parts) + 1:
            continue

        if source_parts[:-1] == module_parts:
            matched.append(document)

    return matched