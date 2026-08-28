"""
The one place the ingest pipeline actually happens:

load
    ->
raw-store
    ->
chunk
    ->
tag with project_id / scope
    ->
embed
    ->
store vectors

The same source_file path is used by both:

    raw_documents
    knowledge_chunks

This is important because the learning-path course layer must be
able to map repository modules to their actual source content.
"""

from pathlib import Path
from typing import List

from .document_loader import load_documents
from .chunk_documents import chunk_documents
from .raw_storage import store_raw_document
from .store_vectors import add_chunks
from .projects import start_new_project


def _source_file_path(
    file_path: str,
) -> str:
    """
    Convert an input file path into a stable repository/source path.

    For repository files, Path.parts is used to preserve the
    meaningful relative path.

    Example:

        data/fastapi/security/oauth2.py

    becomes:

        fastapi/security/oauth2.py

    If the path is already relative to the repository, it is
    preserved as-is.

    Team documentation such as:

        data/team_foundations.md

    remains:

        team_foundations.md
    """

    path = Path(file_path)

    parts = path.parts

    # Remove common local data-directory prefixes.
    cleaned = list(parts)

    while cleaned and cleaned[0] in {
        ".",
        "",
    }:
        cleaned.pop(0)

    if cleaned and cleaned[0].lower() == "data":
        cleaned = cleaned[1:]

    return "/".join(cleaned)


def run_ingest(
    project_id: str,
    file_paths: List[str],
    is_new_project: bool = True,
) -> dict:
    """
    Run the complete ingestion pipeline.

    Source paths are preserved consistently across:

        raw_documents
        knowledge_chunks

    Team documents remain shared across projects.
    Project documents remain project-specific.
    """

    # --------------------------------------------------
    # PROJECT VERSIONING
    # --------------------------------------------------

    if is_new_project:
        start_new_project(project_id)

    if not file_paths:
        return {
            "project_id": project_id,
            "documents_processed": 0,
            "chunks_created": 0,
            "chunks_inserted": 0,
        }

    # --------------------------------------------------
    # LOAD
    # --------------------------------------------------

    documents = load_documents(
        file_paths
    )

    if not documents:
        return {
            "project_id": project_id,
            "documents_processed": 0,
            "chunks_created": 0,
            "chunks_inserted": 0,
        }

    # --------------------------------------------------
    # CHUNK
    # --------------------------------------------------

    chunks = chunk_documents(
        documents
    )

    # --------------------------------------------------
    # TAG PROJECT / TEAM SCOPE
    # --------------------------------------------------

    for chunk in chunks:

        chunk["project_id"] = (
            project_id
            if chunk["scope"] == "project"
            else None
        )

        chunk["status"] = "active"

    # --------------------------------------------------
    # STORE ORIGINAL DOCUMENTS
    # --------------------------------------------------

    for file_path, text in documents:

        source_file = _source_file_path(
            file_path
        )

        filename = Path(
            source_file
        ).name

        scope = (
            "team"
            if filename == "team_foundations.md"
            else "project"
        )

        store_raw_document(
            project_id=(
                project_id
                if scope == "project"
                else None
            ),
            source_file=source_file,
            scope=scope,
            text=text,
        )

    # --------------------------------------------------
    # STORE EMBEDDINGS
    # --------------------------------------------------

    inserted = add_chunks(
        chunks
    )

    return {
        "project_id":
            project_id,

        "documents_processed":
            len(documents),

        "chunks_created":
            len(chunks),

        "chunks_inserted":
            inserted,
    }


if __name__ == "__main__":
    """
    Optional local/manual test.

    The normal entry point is ingest.py or the /ingest API.
    """

    from pathlib import Path

    data_dir = Path("data")

    files = [
        str(path)
        for path in data_dir.rglob("*")
        if path.is_file()
    ]

    result = run_ingest(
        project_id="refund-service",
        file_paths=files,
        is_new_project=True,
    )

    print("\nIngest result:")
    print(result)