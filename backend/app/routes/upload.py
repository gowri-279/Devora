from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
from urllib.parse import urlparse
import requests
import os
from dotenv import load_dotenv

load_dotenv(
    "C:/Users/Administrator/Devora/.env",
    override=True
)

router = APIRouter(tags=["Upload"])


# ==============================
# Configuration
# ==============================

PARSER_URL = "http://10.255.7.46:8000"
KE_URL = os.getenv("KNOWLEDGE_ENGINE_URL")

print(">>> UPLOAD ROUTE KE URL:", KE_URL)
# ==============================
# Request Models
# ==============================

class RepositoryRequest(BaseModel):
    repo_url: str


# ==============================
# Repository Upload + Integration
# ==============================

@router.post("/upload/repository")
def upload_repository(request: RepositoryRequest):

    repo_url = request.repo_url.strip()

    # 1. Validate GitHub URL
    parsed_url = urlparse(repo_url)

    if parsed_url.netloc.lower() not in [
        "github.com",
        "www.github.com"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub repository URL."
        )

    # 2. Call Repo Parser
    try:
        parser_response = requests.post(
            f"{PARSER_URL}/repositories/analyse",
            json={
                "repository_url": repo_url
            },
            timeout=300
        )

        parser_response.raise_for_status()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Repo Parser request failed: {str(e)}"
        )

    # 3. Parse Repo Parser response
    try:
        parser_result = parser_response.json()

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Repo Parser returned an invalid JSON response."
        )

    # 4. Check Parser status
    if parser_result.get("status") != "success":
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Repo Parser failed to analyse the repository.",
                "parser_response": parser_result
            }
        )

    # 5. Extract repository metadata
    repo_metadata = parser_result.get("data")

    if not repo_metadata:
        raise HTTPException(
            status_code=500,
            detail="Repo Parser returned no repository metadata."
        )

    # Debug information
    print("\n========== REPO PARSER DEBUG ==========")
    print("repository:", repo_metadata.get("repository"))
    print("languages:", len(repo_metadata.get("languages", [])))
    print("frameworks:", len(repo_metadata.get("frameworks", [])))
    print("databases:", len(repo_metadata.get("databases", [])))
    print("modules:", len(repo_metadata.get("modules", [])))
    print("files:", len(repo_metadata.get("files", [])))
    print("dependencies:", len(repo_metadata.get("dependencies", [])))
    print("symbols:", len(repo_metadata.get("symbols", [])))
    print("entrypoints:", len(repo_metadata.get("entrypoints", [])))
    print("errors:", len(repo_metadata.get("errors", [])))
    print("=======================================\n")

    # 6. Send metadata to Knowledge Engine
    ke_payload = {
    "project_id": "fastapi",
    "repo_metadata": repo_metadata
}

    try:
        ke_response = requests.post(
            f"{KE_URL}/learning-path",
            json=ke_payload,
            timeout=120
        )

        ke_response.raise_for_status()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Knowledge Engine request failed: {str(e)}"
        )

    # 7. Parse KE response
    try:
        ke_result = ke_response.json()

    except ValueError:
        ke_result = {
            "raw_response": ke_response.text
        }

    # 8. Return complete integration result
    return {
        "message": "Repository analysed and learning path generated successfully.",
        "repo_url": repo_url,
        "parser_status": parser_result.get("status"),
        "repository_metadata": repo_metadata,
        "learning_path": ke_result
    }


# ==============================
# Document Upload
# ==============================

@router.post("/upload/documents")
async def upload_documents(file: UploadFile = File(...)):

    temp_dir = Path("temp/docs")
    temp_dir.mkdir(parents=True, exist_ok=True)

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md"
    }

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