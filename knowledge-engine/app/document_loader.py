"""
File path in -> plain text out.
No chunking, no storage here.
"""

from pathlib import Path
from typing import List, Tuple

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".rst"}


def load_document(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in (".md", ".txt", ".rst"):
        return path.read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        return _load_pdf(path)

    if ext == ".docx":
        return _load_docx(path)

    raise ValueError(
        f"Unsupported file type '{ext}' for {path.name}. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
    )


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _load_docx(path: Path) -> str:
    import docx

    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def load_documents(file_paths: List[str]) -> List[Tuple[str, str]]:
    """
    Returns (file_path, text) tuples.
    Raises on failure — caller handles skipping.
    """

    results = []

    for fp in file_paths:
        text = load_document(fp)

        if text.strip():
            results.append((fp, text))

    return results


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"

    files = [str(p) for p in data_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS]

    docs = load_documents(files)

    for file_path, _ in docs:
        print(f"Loaded: {Path(file_path).name}")

    print(f"\nTotal documents: {len(docs)}")