from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urlparse

router = APIRouter(tags=["Upload"])


class RepositoryRequest(BaseModel):
    repo_url: str


@router.post("/upload/repository")
def upload_repository(request: RepositoryRequest):

    repo_url = request.repo_url.strip()

    # 1. Validate that the URL is a GitHub URL
    parsed_url = urlparse(repo_url)

    if parsed_url.netloc.lower() not in ["github.com", "www.github.com"]:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub repository URL."
        )

    # 2. Check that the repository exists and is accessible
    check_repo = subprocess.run(
        ["git", "ls-remote", repo_url],
        capture_output=True,
        text=True
    )

    if check_repo.returncode != 0:
        raise HTTPException(
            status_code=404,
            detail="Repository does not exist or is not publicly accessible."
        )

    # 3. Create temporary repository folder
    temp_dir = Path("temp")
    repo_dir = temp_dir / "repo"

    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    temp_dir.mkdir(exist_ok=True)

    # 4. Clone the repository
    clone_result = subprocess.run(
        ["git", "clone", repo_url, str(repo_dir)],
        capture_output=True,
        text=True
    )

    if clone_result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail="Repository could not be cloned."
        )

    # 5. Return success
    return {
        "message": "Repository uploaded successfully.",
        "repo_url": repo_url,
        "path": str(repo_dir)
    }


@router.post("/upload/documents")
async def upload_documents(file: UploadFile = File(...)):
    temp_dir = Path("temp/docs")
    temp_dir.mkdir(parents=True, exist_ok=True)

    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    file_path = temp_dir / filename

    content = await file.read()
    file_path.write_bytes(content)

    return {
        "message": "Document uploaded successfully.",
        "filename": filename,
        "path": str(file_path),
        "size": len(content)
    }