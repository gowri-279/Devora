from pathlib import Path
from language_detector import detect_language


def get_file_metadata(file_path: Path, repository_root: Path):
    relative_path = file_path.relative_to(repository_root)

    return {
        "name": file_path.name,
        "path": str(relative_path),
        "extension": file_path.suffix,
        "language": detect_language(str(file_path)),
        "size": file_path.stat().st_size
    }
