from pathlib import Path
import tempfile
import zipfile


def create_zip(repository_path: str) -> str:
    repository = Path(repository_path)

    if not repository.exists() or not repository.is_dir():
        raise ValueError("Repository path must point to an existing directory.")

    artifact_dir = Path(tempfile.mkdtemp(prefix="devora_artifact_"))
    zip_path = artifact_dir / "repository_source.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in repository.rglob("*"):
            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(repository)

            if any(
                part in {
                    ".git",
                    "node_modules",
                    "__pycache__",
                    "venv",
                    ".venv",
                }
                for part in relative_path.parts
            ):
                continue

            zip_file.write(file_path, relative_path)

    return str(zip_path)