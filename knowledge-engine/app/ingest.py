from pathlib import Path
from app.ingest_core import run_ingest


def ingest(project_id: str = "refund-service", is_new_project: bool = True):
    print(f"Starting ingest for project: {project_id}\n")

    files = [str(p) for p in Path("data").glob("*.md")]

    result = run_ingest(project_id, files, is_new_project=is_new_project)

    print(f"Loaded {result['documents_processed']} documents")
    print(f"Created {result['chunks_created']} chunks")
    print(f"Stored {result['chunks_inserted']} vector records")
    print("\nIngest complete!")


if __name__ == "__main__":
    ingest()
