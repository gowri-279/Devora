from pathlib import Path

from app.document_loader import load_documents
from app.chunk_documents import chunk_documents
from app.store_vectors import add_chunks


def ingest(project_id: str = "refund-service"):
    print(f"Starting ingest for project: {project_id}\n")

    # 1. Load documents
    files = [str(p) for p in Path("data").glob("*.md")]
    documents = load_documents(files)

    print(f"Loaded {len(documents)} documents")

    # 2. Chunk documents
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # 3. Attach project_id
    for chunk in chunks:
        if chunk["scope"] == "project":
            chunk["project_id"] = project_id
        else:
            chunk["project_id"] = None

    # 4. Store (embeddings are generated inside add_chunks)
    inserted = add_chunks(chunks)

    print(f"Stored {inserted} vector records")
    print("\nIngest complete!")


if __name__ == "__main__":
    ingest()