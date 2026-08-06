from pathlib import Path
from typing import List, Tuple
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.document_loader import load_documents

# Chunking configuration
CHUNK_SIZE = 380
CHUNK_OVERLAP = 80

# Sections whose body content is shorter than this are treated as "stub"
# sections (e.g. a "Getting Started" heading that just points at the next
# few sections with no real content of its own) and get merged forward
# into the next section instead of standing alone as a weak, low-content
# chunk.
MIN_SECTION_CONTENT_CHARS = 80

# Fallback splitter (used only if a section is too large)
fallback_splitter = RecursiveCharacterTextSplitter(
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
        "team_foundations.md"
    }

    return "team" if filename in team_docs else "project"


def split_markdown_sections(text: str):
    """
    Split markdown into semantic sections.
    Returns: (section_id, section_title, section_text)
    """

    pattern = r"(?m)^(#{1,6}\s.*)$"
    parts = re.split(pattern, text)

    sections = []

    if parts and parts[0].strip():
        sections.append(("intro", "Introduction", parts[0].strip()))

    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1].strip()

        section_title = re.sub(r"^#{1,6}\s*", "", heading).strip()
        section_id = section_title.lower().replace(" ", "_")

        section_text = f"{heading}\n\n{body}".strip()

        sections.append((section_id, section_title, section_text))
        i += 2

    return sections


def merge_stub_sections(sections, min_content_chars: int = MIN_SECTION_CONTENT_CHARS):
    """
    Merges sections that are mostly just a heading with little to no real
    content (e.g. a "Getting Started" heading that's just a one-line
    pointer to the sections that follow it) into the NEXT section, so
    retrieval doesn't return a near-empty chunk as its top match.

    This matters a lot for flat-hierarchy docs (every heading is #, no
    nesting) where there's no structural signal telling you that
    "Prerequisites" and "Local Setup Overview" are logically children of
    "Getting Started" — merging by content length is a simple heuristic
    that works without needing that structure to be explicit.
    """
    merged = []
    i = 0
    while i < len(sections):
        section_id, title, text = sections[i]
        # Rough body length: strip the heading line itself before measuring.
        body_only = re.sub(r"(?m)^#{1,6}\s.*$", "", text).strip()

        is_last = i == len(sections) - 1
        if len(body_only) < min_content_chars and not is_last:
            next_id, next_title, next_text = sections[i + 1]
            combined_text = f"{text}\n\n{next_text}".strip()
            combined_title = f"{title} / {next_title}"
            merged.append((next_id, combined_title, combined_text))
            i += 2
        else:
            merged.append((section_id, title, text))
            i += 1
    return merged


def chunk_text(text: str):
    """
    Markdown-aware chunking with section metadata.
    Returns: (section_id, section_title, chunk_text)
    """

    sections = split_markdown_sections(text)
    sections = merge_stub_sections(sections)

    chunks = []

    for section_id, section_title, section in sections:
        if len(section) <= CHUNK_SIZE:
            chunks.append((section_id, section_title, section.strip()))
        else:
            split_chunks = fallback_splitter.split_text(section)

            for c in split_chunks:
                if c.strip():
                    chunks.append((section_id, section_title, c.strip()))

    return chunks


def chunk_documents(documents: List[Tuple[str, str]]) -> List[dict]:
    """
    Convert loaded documents into structured chunks ready for embeddings.

    Each chunk carries BOTH:
    - metadata.chunk_index: position within its own section (kept for
      backward compatibility with search.py's reconstruct_section()).
    - metadata.doc_position: a GLOBAL running index across the whole
      document, regardless of section. This is what powers neighbor-window
      retrieval in search.py — since it's assigned deterministically at
      chunk time, at query time you never have to guess whether a chunk
      is "the next one" — you just look up doc_position +/- N.
    """

    all_chunks = []

    for file_path, text in documents:
        filename = Path(file_path).name
        scope = infer_scope(filename)

        pieces = chunk_text(text)

        section_counters = {}
        for doc_position, (section_id, section_title, piece) in enumerate(pieces):
            chunk_index = section_counters.get(section_id, 0)
            section_counters[section_id] = chunk_index + 1

            all_chunks.append({
                "chunk_id": f"{filename}::{doc_position}",
                "source_file": filename,
                "text": piece,
                "scope": scope,
                "metadata": {
                    "source_file": filename,
                    "chunk_index": chunk_index,
                    "doc_position": doc_position,
                    "scope": scope,
                    "section_id": section_id,
                    "section_title": section_title,
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
        print(f"[{c['scope']}] {c['chunk_id']} (doc_position={c['metadata']['doc_position']})\n")
        print(c["text"])
        print("\n" + "-" * 80 + "\n")