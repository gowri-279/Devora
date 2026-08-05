import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.document_loader import load_documents
from app.chunk_documents import chunk_documents
from app.embeddings import embed_texts

files = [str(p) for p in Path("data").glob("*.md")]

docs = load_documents(files)

chunks = chunk_documents(docs)

texts = [c["text"] for c in chunks]

vectors = embed_texts(texts)

print(f"Chunks: {len(chunks)}")
print(f"Vectors: {len(vectors)}")
print(f"Dimension: {len(vectors[0])}")

print("\nFirst vector (first 5 values):")
print(vectors[0][:5])