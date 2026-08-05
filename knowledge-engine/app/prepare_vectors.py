from pathlib import Path
from app.document_loader import load_documents
from app.chunk_documents import chunk_documents
from app.embeddings import embed_texts

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
    records.append({
        **chunk,
        "embedding": vector
    })

print(f"Prepared {len(records)} vector records")
print(f"Embedding dimension: {len(records[0]['embedding'])}")

print(" Sample record:") 
sample = records[0] 

print({ 
    "chunk_id": sample["chunk_id"], 
    "source_file": sample["source_file"], 
    "scope": sample["scope"], 
    "text_preview": sample["text"][:80], 
    "metadata": sample["metadata"], 
    "embedding_length": len(sample["embedding"]) 
})