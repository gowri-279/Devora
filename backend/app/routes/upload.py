from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
from urllib.parse import urlparse
import os
import tempfile
import zipfile

import requests
from dotenv import load_dotenv
from app.services.project import save_project, get_project

load_dotenv()

router = APIRouter(
    prefix="/api",
    tags=["Upload"],
)

PARSER_URL = os.getenv(
    "REPOSITORY_PARSER_URL",
    "http://127.0.0.1:8003",
).rstrip("/")

KE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> UPLOAD ROUTE PARSER URL:", PARSER_URL)
print(">>> UPLOAD ROUTE KE URL:", KE_URL)


class RepositoryRequest(BaseModel):
    repo_url: str


SUPPORTED_SOURCE_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".xml",
    ".ini",
    ".cfg",
    ".sh",
    ".bash",
}


def _resolve_artifact_url(
    artifact_url: str,
) -> str:
    """
    Convert a relative Parser artifact URL into
    an absolute URL.
    """

    parsed = urlparse(artifact_url)

    if parsed.scheme and parsed.netloc:
        return artifact_url

    return f"{PARSER_URL}/{artifact_url.lstrip('/')}"


def _download_and_extract_artifact(
    artifact_url: str,
) -> tuple[Path, tempfile.TemporaryDirectory]:
    """
    Download the repository source ZIP and extract it.

    The ZIP contains paths relative to the repository root.
    Those paths are preserved when extracting.
    """

    temp_dir = tempfile.TemporaryDirectory(
        prefix="devora_repo_"
    )

    temp_path = Path(temp_dir.name)

    zip_path = temp_path / "repository_source.zip"
    extract_path = temp_path / "source"

    extract_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with requests.get(
            artifact_url,
            stream=True,
            timeout=120,
        ) as response:

            response.raise_for_status()

            with zip_path.open("wb") as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)

        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as archive:

            archive.extractall(
                extract_path
            )

    except Exception:
        temp_dir.cleanup()
        raise

    return extract_path, temp_dir


def _collect_source_files(
    repository_root: Path,
) -> list[str]:
    """
    Collect only source/configuration files that
    the Knowledge Engine document loader supports.

    Paths are returned relative to the extracted
    repository root so KE can preserve repository
    source paths.
    """

    source_files = []

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
            for part in path.relative_to(
                repository_root
            ).parts
        ):
            continue

        if path.suffix.lower() not in (
            SUPPORTED_SOURCE_EXTENSIONS
        ):
            continue

        if path.stat().st_size > 1024 * 1024:
            continue

        source_files.append(
            str(path)
        )

    source_files.sort()

    return source_files


@router.post("/upload/repository")
def upload_repository(
    request: RepositoryRequest,
):

    repo_url = request.repo_url.strip()

    parsed_url = urlparse(
        repo_url
    )

    if parsed_url.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide a valid "
                "GitHub repository URL."
            ),
        )

    if not KE_URL:
        raise HTTPException(
            status_code=500,
            detail=(
                "KNOWLEDGE_ENGINE_URL is not configured."
            ),
        )

    # --------------------------------------------------
    # REPOSITORY PARSER
    # --------------------------------------------------

    try:

        parser_response = requests.post(
            f"{PARSER_URL}/repositories/analyse",
            json={
                "repository_url": repo_url
            },
            timeout=300,
        )

        parser_response.raise_for_status()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=502,
            detail=(
                f"Repo Parser request failed: {str(e)}"
            ),
        )

    try:

        parser_result = (
            parser_response.json()
        )

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail=(
                "Repo Parser returned "
                "an invalid JSON response."
            ),
        )

    if parser_result.get("status") != "success":

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Repo Parser failed to "
                    "analyse the repository."
                ),
                "parser_response": parser_result,
            },
        )

    repo_metadata = parser_result.get(
        "data"
    )

    if not repo_metadata:

        raise HTTPException(
            status_code=500,
            detail=(
                "Repo Parser returned "
                "no repository metadata."
            ),
        )

    source_artifact = (
        repo_metadata.get(
            "source_artifact"
        )
    )

    if not source_artifact:

        raise HTTPException(
            status_code=500,
            detail=(
                "Repo Parser did not return "
                "a source artifact."
            ),
        )

    artifact_url = source_artifact.get(
        "url"
    )

    if not artifact_url:

        raise HTTPException(
            status_code=500,
            detail=(
                "Repo Parser returned an "
                "invalid source artifact."
            ),
        )

    artifact_url = _resolve_artifact_url(
        artifact_url
    )

    print(
        "\n========== REPO PARSER =========="
    )
    print(
        "repository:",
        repo_metadata.get(
            "repository"
        ),
    )
    print(
        "languages:",
        len(
            repo_metadata.get(
                "languages",
                [],
            )
        ),
    )
    print(
        "modules:",
        len(
            repo_metadata.get(
                "modules",
                [],
            )
        ),
    )
    print(
        "files:",
        len(
            repo_metadata.get(
                "files",
                [],
            )
        ),
    )
    print(
        "dependencies:",
        len(
            repo_metadata.get(
                "dependencies",
                [],
            )
        ),
    )
    print(
        "symbols:",
        len(
            repo_metadata.get(
                "symbols",
                [],
            )
        ),
    )
    print(
        "artifact:",
        artifact_url,
    )
    print(
        "=================================\n"
    )

    # --------------------------------------------------
    # SOURCE ARTIFACT
    # --------------------------------------------------

    temp_dir = None

    try:

        try:

            extracted_root, temp_dir = (
                _download_and_extract_artifact(
                    artifact_url
                )
            )

        except requests.RequestException as e:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Repository source artifact "
                    f"download failed: {str(e)}"
                ),
            )

        except zipfile.BadZipFile:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Repository Parser returned "
                    "an invalid ZIP artifact."
                ),
            )

        source_files = _collect_source_files(
            extracted_root
        )

        if not source_files:

            raise HTTPException(
                status_code=500,
                detail=(
                    "No supported source files "
                    "were found in the repository artifact."
                ),
            )

        print(
            ">>> SOURCE FILES FOR KE:",
            len(source_files)
        )

        # --------------------------------------------------
        # PROJECT ID
        # --------------------------------------------------

        repository_name = (
            repo_metadata.get(
                "repository"
            )
            or parsed_url.path.strip(
                "/"
            ).split("/")[-1]
            or "repository"
        )

        project_id = Path(
            repository_name
        ).name.lower()

        # --------------------------------------------------
        # PERSIST PROJECT REPOSITORY METADATA
        # --------------------------------------------------

        repo_metadata["repo_url"] = repo_url

        save_project(
            project_id=project_id,
            repo_metadata=repo_metadata,
        )

        print(
            ">>> PROJECT METADATA SAVED:",
            project_id,
        )

        # --------------------------------------------------
        # KNOWLEDGE ENGINE INGESTION
        # --------------------------------------------------

        try:

            ingest_response = requests.post(
                f"{KE_URL}/ingest",
                json={
                    "project_id": project_id,
                    "file_paths": source_files,
                    "is_new_project": True,
                },
                timeout=900,
            )

            ingest_response.raise_for_status()

        except requests.RequestException as e:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Knowledge Engine ingestion "
                    f"failed: {str(e)}"
                ),
            )

        try:

            ingest_result = (
                ingest_response.json()
            )

        except ValueError:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Knowledge Engine returned "
                    "an invalid ingestion response."
                ),
            )

        print(
            ">>> KE INGESTION:",
            ingest_result
        )

        # --------------------------------------------------
        # LEARNING PATH
        # --------------------------------------------------

        try:

            learning_response = requests.post(
                f"{KE_URL}/learning-path",
                json={
                    "project_id": project_id,
                    "repo_metadata": repo_metadata,
                },
                timeout=300,
            )

            learning_response.raise_for_status()

        except requests.RequestException as e:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Knowledge Engine learning-path "
                    f"request failed: {str(e)}"
                ),
            )

        try:

            learning_result = (
                learning_response.json()
            )

        except ValueError:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Knowledge Engine returned "
                    "an invalid learning-path response."
                ),
            )

        print(
            ">>> LEARNING PATH GENERATED"
        )

        return {
            "message": (
                "Repository analysed, source "
                "ingested, and learning path "
                "generated successfully."
            ),
            "repo_url": repo_url,
            "project_id": project_id,
            "parser_status": parser_result.get(
                "status"
            ),
            "repository_metadata": {
                "repository": repo_metadata.get(
                    "repository"
                ),
                "languages": repo_metadata.get(
                    "languages",
                    [],
                ),
                "module_count": len(
                    repo_metadata.get(
                        "modules",
                        [],
                    )
                ),
                "file_count": len(
                    repo_metadata.get(
                        "files",
                        [],
                    )
                ),
                "dependency_count": len(
                    repo_metadata.get(
                        "dependencies",
                        [],
                    )
                ),
                "entrypoint_count": len(
                    repo_metadata.get(
                        "entrypoints",
                        [],
                    )
                ),
                "symbol_count": len(
                    repo_metadata.get(
                        "symbols",
                        [],
                    )
                ),
                "tech_stack": repo_metadata.get(
                    "tech_stack"
                ),
            },
            "ingestion": ingest_result,
            "learning_path": learning_result,
        }

    finally:

        if temp_dir is not None:
            temp_dir.cleanup()


@router.post("/upload/documents")
async def upload_documents(
    project_id: str,
    file: UploadFile = File(...),
):
    """
    Upload and ingest a project-specific document.

    Documents are stored under the selected project and then
    added to the existing Knowledge Engine project knowledge
    base without creating a new project version.
    """

    project_id = project_id.strip()

    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required.",
        )

    if not KE_URL:
        raise HTTPException(
            status_code=500,
            detail="KNOWLEDGE_ENGINE_URL is not configured.",
        )

    project = get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_id}' was not found.",
        )

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".rst",
    }

    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="A document filename is required.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types: {sorted(allowed_extensions)}"
            ),
        )

    # Keep uploaded documents separated by project so that
    # project knowledge remains isolated.
    project_dir = (
        Path("temp/docs") / project_id
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = project_dir / filename

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded document is empty.",
        )

    file_path.write_bytes(content)

    print(
        ">>> PROJECT DOCUMENT SAVED:",
        project_id,
        file_path,
    )

    try:
        with file_path.open("rb") as document_file:
            ke_response = requests.post(
                f"{KE_URL}/ingest/upload",
                data={
                    "project_id": project_id,
                    "is_new_project": "false",
                },
                files={
                    "file": (
                        filename,
                        document_file,
                        file.content_type or "application/octet-stream",
                    ),
                },
                timeout=900,
            )
            ke_response.raise_for_status()
            ingest_result = ke_response.json()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Knowledge Engine document ingestion failed: "
                f"{str(exc)}"
            ),
        )

    print(
        ">>> PROJECT DOCUMENT INGESTED:",
        ingest_result,
    )

    # Regenerate the learning path using the existing repository
    # metadata plus the newly ingested project knowledge.
    repo_metadata = project.get(
        "repo_metadata",
        {},
    )

    learning_result = None

    if repo_metadata:
        try:
            learning_response = requests.post(
                f"{KE_URL}/learning-path",
                json={
                    "project_id": project_id,
                    "repo_metadata": repo_metadata,
                },
                timeout=300,
            )

            learning_response.raise_for_status()
            learning_result = learning_response.json()

        except requests.RequestException as exc:
            # The document itself has already been ingested.
            # Do not report the upload as a total failure just
            # because curriculum regeneration failed.
            print(
                ">>> LEARNING PATH REGENERATION FAILED:",
                exc,
            )

    return {
        "message": "Document uploaded and ingested successfully.",
        "project_id": project_id,
        "filename": filename,
        "path": str(file_path),
        "size": len(content),
        "ingestion": ingest_result,
        "learning_path": learning_result,
    }


@router.get("/documents")
def get_documents(
    project_id: str,
    include_archived: bool = False,
):
    """
    Return project documentation from the Knowledge Engine.

    The frontend talks only to the Backend. The Backend
    proxies the request to the Knowledge Engine.
    """

    project_id = project_id.strip()

    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required.",
        )

    if not KE_URL:
        raise HTTPException(
            status_code=500,
            detail="KNOWLEDGE_ENGINE_URL is not configured.",
        )

    project = get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_id}' was not found.",
        )

    try:
        response = requests.get(
            f"{KE_URL}/documents",
            params={
                "project_id": project_id,
                "include_archived": include_archived,
            },
            timeout=60,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Knowledge Engine document retrieval failed: "
                f"{str(exc)}"
            ),
        )

    try:
        documents_result = response.json()

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Knowledge Engine returned "
                "an invalid documents response."
            ),
        )

    return documents_result


@router.get("/projects/{project_id}/repository")
def get_project_repository(project_id: str):
    project_id = project_id.strip()

    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required.",
        )

    project = get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_id}' was not found.",
        )

    repo_metadata = project.get("repo_metadata", {})

    return {
    "project_id": project_id,
    "repo_url": (
        repo_metadata.get("repo_url")
        or repo_metadata.get("repository")
    ),
    "repository": repo_metadata.get("repository"),
}