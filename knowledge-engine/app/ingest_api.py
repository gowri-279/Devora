from pydantic import BaseModel
from app.document_loader import load_documents
from app.chunk_documents import chunk_documents
from app.store_vectors import add_chunks


class IngestRequest(BaseModel):
    project_id: str
    file_paths: list[str]


def ingest_files(req: IngestRequest):
    documents = load_documents(req.file_paths)

    chunks = chunk_documents(documents)

    for c in chunks:
        c["project_id"] = req.project_id

    add_chunks(chunks)

    return {
        "project_id": req.project_id,
        "documents_processed": len(documents),
        "chunks_created": len(chunks)
    }