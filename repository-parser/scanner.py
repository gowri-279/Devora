from pathlib import Path
from metadata import get_file_metadata


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv"
}

IGNORED_FILE_NAMES = {
    "wtf.jpg",
    "random.md",
    "hello.txt"
}


def _is_ignored_path(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts

    if any(part in IGNORED_DIRECTORIES for part in relative_parts):
        return True

    if any(part.endswith(".not") for part in relative_parts):
        return True

    return path.name.lower() in IGNORED_FILE_NAMES


def scan_repository(repository_path: str):
    root = Path(repository_path)

    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if _is_ignored_path(path, root):
            continue

        files.append(
            get_file_metadata(path, root)
        )

    return files