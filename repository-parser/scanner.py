from pathlib import Path
from metadata import get_file_metadata


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
}

IGNORED_FILE_NAMES = {
    "wtf.jpg",
    "random.md",
    "hello.txt",
}

MAX_SOURCE_FILE_SIZE = 1_000_000


def _is_ignored_path(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts

    if any(part in IGNORED_DIRECTORIES for part in relative_parts):
        return True

    if any(part.endswith(".not") for part in relative_parts):
        return True

    return path.name.lower() in IGNORED_FILE_NAMES


def _read_source_content(path: Path) -> str | None:
    if path.stat().st_size > MAX_SOURCE_FILE_SIZE:
        return None

    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return None


def scan_repository(repository_path: str):
    root = Path(repository_path)
    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if _is_ignored_path(path, root):
            continue

        file_info = get_file_metadata(path, root)
        file_info["content"] = _read_source_content(path)

        files.append(file_info)

    return files