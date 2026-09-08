"""
Repository source-artifact ingestion for DEVORA Knowledge Engine.

Downloads a repository ZIP produced by the Repository Parser,
extracts it safely, filters supported source files, and reuses
the existing ingestion pipeline.
"""

from pathlib import Path
import tempfile
import zipfile

import requests

from app.document_loader import SUPPORTED_EXTENSIONS
from app.ingest_core import run_ingest


MAX_ARTIFACT_SIZE = 100 * 1024 * 1024  # 100 MB
DOWNLOAD_TIMEOUT = 120


def _safe_extract(
    zip_file: zipfile.ZipFile,
    destination: Path,
) -> None:
    """
    Extract a ZIP while preventing path traversal.
    """

    destination = destination.resolve()

    for member in zip_file.infolist():
        member_path = (destination / member.filename).resolve()

        if (
            member_path != destination
            and destination not in member_path.parents
        ):
            raise ValueError(
                f"Unsafe ZIP path detected: {member.filename}"
            )

    zip_file.extractall(destination)


def _collect_source_files(
    repository_root: Path,
) -> list[str]:
    """
    Collect files supported by the Knowledge Engine loader.

    Paths returned here are absolute so the existing ingestion
    pipeline can load them directly.
    """

    files = []

    for path in repository_root.rglob("*"):
        if not path.is_file():
            continue

        if any(
            part in {
                ".git",
                "node_modules",
                "__pycache__",
                "venv",
                ".venv",
            }
            for part in path.relative_to(repository_root).parts
        ):
            continue

        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(str(path))

    return files


def ingest_repository_artifact(
    project_id: str,
    artifact_url: str,
    is_new_project: bool = True,
) -> dict:
    """
    Download, safely extract, and ingest a repository source artifact.
    """

    response = requests.get(
        artifact_url,
        timeout=DOWNLOAD_TIMEOUT,
        stream=True,
    )

    response.raise_for_status()

    content_length = response.headers.get("content-length")

    if content_length and int(content_length) > MAX_ARTIFACT_SIZE:
        raise ValueError(
            "Repository artifact exceeds the maximum allowed size."
        )

    with tempfile.TemporaryDirectory(
        prefix="devora_repository_"
    ) as temp_dir:

        temp_root = Path(temp_dir)

        zip_path = temp_root / "repository.zip"
        repository_root = temp_root / "repository"

        downloaded_size = 0

        with zip_path.open("wb") as output:
            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if not chunk:
                    continue

                downloaded_size += len(chunk)

                if downloaded_size > MAX_ARTIFACT_SIZE:
                    raise ValueError(
                        "Repository artifact exceeds the maximum allowed size."
                    )

                output.write(chunk)

        repository_root.mkdir()

        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as zip_file:

            if zip_file.testzip() is not None:
                raise ValueError(
                    "Repository artifact is a corrupted ZIP file."
                )

            _safe_extract(
                zip_file,
                repository_root,
            )

        file_paths = _collect_source_files(
            repository_root
        )

        if not file_paths:
            raise ValueError(
                "Repository artifact contains no supported source files."
            )

        return run_ingest(
            project_id=project_id,
            file_paths=file_paths,
            is_new_project=is_new_project,
            source_root=str(repository_root),
        )