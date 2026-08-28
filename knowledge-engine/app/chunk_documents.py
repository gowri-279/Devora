from pathlib import Path
from typing import List, Tuple
import re
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.document_loader import load_documents


# ============================================================
# CHUNKING CONFIGURATION
# ============================================================

CHUNK_SIZE = 380
CHUNK_OVERLAP = 80

MIN_SECTION_CONTENT_CHARS = 80


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
        " ",
    ],
)


# ============================================================
# SOURCE PATH HANDLING
# ============================================================

def _common_source_root(file_paths: List[str]) -> str:
    """
    Determine the common directory shared by all ingested files.

    For a cloned repository such as:

        /tmp/repository/
            fastapi/
            fastapi/security/
            fastapi/openapi/

    the common root becomes:

        /tmp/repository

    This allows us to preserve paths such as:

        fastapi/security/oauth2.py

    instead of reducing everything to:

        oauth2.py

    For ordinary uploaded documents:

        /tmp/docs/README.md
        /tmp/docs/architecture.md

    the common root becomes:

        /tmp/docs

    and the stored source files remain:

        README.md
        architecture.md
    """

    if not file_paths:
        return ""

    absolute_paths = [
        os.path.abspath(path)
        for path in file_paths
    ]

    try:
        return os.path.commonpath(
            absolute_paths
        )
    except ValueError:
        # Different drives on Windows, for example.
        return ""


def source_file_path(
    file_path: str,
    common_root: str,
) -> str:
    """
    Return the repository/document-relative source path.

    The path is normalized to '/' so the value is deterministic
    across operating systems.
    """

    absolute_path = os.path.abspath(
        file_path
    )

    if common_root:
        try:
            relative = os.path.relpath(
                absolute_path,
                common_root,
            )

            if relative != ".":
                return Path(
                    relative
                ).as_posix()

        except ValueError:
            pass

    return Path(
        file_path
    ).name


# ============================================================
# SCOPE
# ============================================================

def infer_scope(filename: str) -> str:
    """
    Team-level docs are reusable across projects.
    Project-level docs are specific to the current project.
    """

    team_docs = {
        "team_foundations.md",
    }

    return (
        "team"
        if Path(filename).name in team_docs
        else "project"
    )


# ============================================================
# MARKDOWN SECTIONING
# ============================================================

def split_markdown_sections(text: str):
    """
    Split markdown into semantic sections.

    Returns:

        (section_id, section_title, section_text)
    """

    pattern = r"(?m)^(#{1,6}\s.*)$"

    parts = re.split(
        pattern,
        text,
    )

    sections = []

    if parts and parts[0].strip():
        sections.append(
            (
                "intro",
                "Introduction",
                parts[0].strip(),
            )
        )

    i = 1

    while i < len(parts) - 1:

        heading = parts[i].strip()
        body = parts[i + 1].strip()

        section_title = re.sub(
            r"^#{1,6}\s*",
            "",
            heading,
        ).strip()

        section_id = (
            section_title
            .lower()
            .replace(" ", "_")
        )

        section_text = (
            f"{heading}\n\n{body}"
        ).strip()

        sections.append(
            (
                section_id,
                section_title,
                section_text,
            )
        )

        i += 2

    return sections


# ============================================================
# STUB SECTION MERGING
# ============================================================

def merge_stub_sections(
    sections,
    min_content_chars: int = MIN_SECTION_CONTENT_CHARS,
):
    """
    Merge sections that contain very little actual content
    into the following section.

    This avoids producing weak chunks containing only a heading
    or a short pointer.
    """

    merged = []

    i = 0

    while i < len(sections):

        section_id, title, text = sections[i]

        body_only = re.sub(
            r"(?m)^#{1,6}\s.*$",
            "",
            text,
        ).strip()

        is_last = (
            i == len(sections) - 1
        )

        if (
            len(body_only) < min_content_chars
            and not is_last
        ):

            next_id, next_title, next_text = (
                sections[i + 1]
            )

            combined_text = (
                f"{text}\n\n{next_text}"
            ).strip()

            combined_title = (
                f"{title} / {next_title}"
            )

            merged.append(
                (
                    next_id,
                    combined_title,
                    combined_text,
                )
            )

            i += 2

        else:

            merged.append(
                (
                    section_id,
                    title,
                    text,
                )
            )

            i += 1

    return merged


# ============================================================
# CHUNK SINGLE DOCUMENT
# ============================================================

def chunk_text(text: str):
    """
    Markdown-aware chunking with section metadata.

    Returns:

        (section_id, section_title, chunk_text)
    """

    sections = split_markdown_sections(
        text
    )

    sections = merge_stub_sections(
        sections
    )

    chunks = []

    for (
        section_id,
        section_title,
        section,
    ) in sections:

        if len(section) <= CHUNK_SIZE:

            chunks.append(
                (
                    section_id,
                    section_title,
                    section.strip(),
                )
            )

        else:

            split_chunks = (
                fallback_splitter.split_text(
                    section
                )
            )

            for c in split_chunks:

                if c.strip():

                    chunks.append(
                        (
                            section_id,
                            section_title,
                            c.strip(),
                        )
                    )

    return chunks


# ============================================================
# CHUNK ALL DOCUMENTS
# ============================================================

def chunk_documents(
    documents: List[Tuple[str, str]]
) -> List[dict]:
    """
    Convert loaded documents into structured chunks.

    Important:

    The original relative source path is preserved.

    Example:

        fastapi/security/oauth2.py

    remains:

        fastapi/security/oauth2.py

    instead of becoming only:

        oauth2.py

    Each chunk carries:

    - source_file
    - text
    - scope
    - metadata.chunk_index
    - metadata.doc_position
    - metadata.section_id
    - metadata.section_title
    """

    all_chunks = []

    if not documents:
        return all_chunks

    file_paths = [
        file_path
        for file_path, _ in documents
    ]

    common_root = _common_source_root(
        file_paths
    )

    for file_path, text in documents:

        source_file = source_file_path(
            file_path,
            common_root,
        )

        scope = infer_scope(
            source_file
        )

        pieces = chunk_text(
            text
        )

        section_counters = {}

        for (
            doc_position,
            (
                section_id,
                section_title,
                piece,
            ),
        ) in enumerate(pieces):

            chunk_index = (
                section_counters.get(
                    section_id,
                    0,
                )
            )

            section_counters[
                section_id
            ] = chunk_index + 1

            all_chunks.append({

                "chunk_id":
                    f"{source_file}::{doc_position}",

                "source_file":
                    source_file,

                "text":
                    piece,

                "scope":
                    scope,

                "metadata": {

                    "source_file":
                        source_file,

                    "chunk_index":
                        chunk_index,

                    "doc_position":
                        doc_position,

                    "scope":
                        scope,

                    "section_id":
                        section_id,

                    "section_title":
                        section_title,
                },
            })

    return all_chunks


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    data_dir = Path("data")

    files = [
        str(p)
        for p in data_dir.rglob("*")
        if (
            p.is_file()
            and p.suffix.lower()
            in {
                ".md",
                ".txt",
                ".pdf",
                ".docx",
                ".rst",
            }
        )
    ]

    documents = load_documents(
        files
    )

    chunks = chunk_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks\n"
    )

    for c in chunks[:5]:

        print(
            f"[{c['scope']}] "
            f"{c['chunk_id']} "
            f"(doc_position="
            f"{c['metadata']['doc_position']})\n"
        )

        print(
            c["text"]
        )

        print(
            "\n"
            + "-" * 80
            + "\n"
        )