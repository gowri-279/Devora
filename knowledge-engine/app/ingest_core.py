"""
The one place the ingest pipeline actually happens: load -> raw-store ->
chunk -> tag with project_id (respecting scope) -> embed + store vectors.

ingest.py (CLI script) and ingest_api.py (FastAPI endpoint) both call
run_ingest() instead of each reimplementing the pipeline — that
duplication is exactly what caused ingest_api.py to drift and mistag
team-scope chunks with a project_id. Fix it once, here.
"""

from typing import List, Optional

from .document_loader import load_documents
from .chunk_documents import chunk_documents
from .raw_storage import store_raw_document
from .store_vectors import add_chunks
from .projects import start_new_project


def run_ingest(project_id: str, file_paths: List[str], is_new_project: bool = True) -> dict:
    """
    is_new_project: True (default) archives whatever project was
    previously active before ingesting — matches your "new repo cloned ->
    archive old, start fresh" requirement. Pass False if you're just
    adding more docs to the CURRENTLY active project (no archiving).
    """
    if is_new_project:
        start_new_project(project_id)

    documents = load_documents(file_paths)  # list of (file_path, text)

    chunks = chunk_documents(documents)

    # Tag each chunk with project_id, respecting scope: team-scope docs
    # get project_id=None so they stay shared across every project (this
    # is the exact bug that existed in the old ingest_api.py — every
    # chunk needs to go through this branch, not just the CLI path).
    for chunk in chunks:
        chunk["project_id"] = project_id if chunk["scope"] == "project" else None
        chunk["status"] = "active"

    # Store the untouched original text alongside the chunked version.
    for file_path, text in documents:
        from pathlib import Path
        filename = Path(file_path).name
        scope = "team" if filename == "team_foundations.md" else "project"
        store_raw_document(
            project_id=project_id if scope == "project" else None,
            source_file=filename,
            scope=scope,
            text=text,
        )

    inserted = add_chunks(chunks)

    return {
        "project_id": project_id,
        "documents_processed": len(documents),
        "chunks_created": len(chunks),
        "chunks_inserted": inserted,
    }
