from pathlib import Path
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.document_loader import load_documents

# Chunking configuration
CHUNK_SIZE = 380
CHUNK_OVERLAP = 80

# Semantic-first splitting (prevents cutting words in half)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        ": ",
        " "
    ]
)

def infer_scope(filename: str) -> str:
    """
    Team-level docs are reusable across projects.
    Project-level docs are specific to the current project.
    """

    team_docs = {
        "team_foundations.md",
        "calcom_CONTRIBUTING.md"
    }

    return "team" if filename in team_docs else "project"

def chunk_text(text: str) -> List[str]:
    """Split text into overlapping semantic chunks."""

    return [c.strip() for c in splitter.split_text(text) if c.strip()]

def chunk_documents(documents: List[Tuple[str, str]]) -> List[dict]:
    """
    Convert loaded documents into structured chunks ready for embeddings.
    """

    all_chunks = []

    for file_path, text in documents:
        filename = Path(file_path).name
        scope = infer_scope(filename)

        pieces = chunk_text(text)

        for i, piece in enumerate(pieces):
            all_chunks.append({
                "chunk_id": f"{filename}::{i}",
                "source_file": filename,
                "text": piece,
                "scope": scope,
                "metadata": {
                    "source_file": filename,
                    "chunk_index": i,
                    "scope": scope
                }
            })

    return all_chunks

if __name__ == "__main__":
    data_dir = Path("data")

    files = [str(p) for p in data_dir.glob("*.md")]

    documents = load_documents(files)

    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks\n")

    # Preview first 5 chunks
    for c in chunks[:5]:
        print(f"[{c['scope']}] {c['chunk_id']}")
        print(c["text"])
        print("-" * 50)