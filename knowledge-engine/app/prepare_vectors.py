from pathlib import Path
from app.document_loader import load_documents
from app.chunk_documents import chunk_documents
from app.embeddings import embed_texts

# Active project for this ingest run
PROJECT_ID = "refund-service"

# Load documents
files = [str(p) for p in Path("data").glob("*.md")]
docs = load_documents(files)

# Create chunks
chunks = chunk_documents(docs)

# Generate embeddings
texts = [c["text"] for c in chunks]
vectors = embed_texts(texts)

# Combine chunk + vector
records = []

for chunk, vector in zip(chunks, vectors):

    # Team docs are shared across all projects
    if chunk["scope"] == "team":
        project_id = None
    else:
        project_id = PROJECT_ID

    records.append({
        "project_id": project_id,
        **chunk,
        "embedding": vector
    })

print(f"Prepared {len(records)} vector records")
print(f"Embedding dimension: {len(records[0]['embedding'])}")

print("\nSample record:")
sample = records[0]

print({
    "project_id": sample["project_id"],
    "chunk_id": sample["chunk_id"],
    "source_file": sample["source_file"],
    "scope": sample["scope"],
    "text_preview": sample["text"][:80],
    "metadata": sample["metadata"],
    "embedding_length": len(sample["embedding"])
})