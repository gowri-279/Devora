from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.ingest_core import run_ingest


router = APIRouter()


class IngestRequest(BaseModel):
    project_id: str
    file_paths: List[str]
    is_new_project: bool = True


def ingest_files(req: IngestRequest):
    return run_ingest(
        req.project_id,
        req.file_paths,
        is_new_project=req.is_new_project,
    )


@router.post("/ingest/upload")
async def ingest_uploaded_file(
    project_id: str = Form(...),
    is_new_project: bool = Form(False),
    file: UploadFile = File(...),
):
    """
    Receive a document from another DEVORA service.

    The Backend owns the user's uploaded file.
    The Knowledge Engine receives the file bytes,
    stores them temporarily in its own process,
    runs the normal ingestion pipeline, and then
    removes the temporary file.

    This avoids sharing filesystem paths between services.
    """

    project_id = project_id.strip()

    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required.",
        )

    filename = Path(
        file.filename or ""
    ).name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    suffix = Path(filename).suffix

    with TemporaryDirectory(
        prefix="devora_document_"
    ) as temp_dir:

        temp_path = (
            Path(temp_dir) / filename
        )

        temp_path.write_bytes(content)

        result = run_ingest(
            project_id=project_id,
            file_paths=[str(temp_path)],
            is_new_project=is_new_project,
        )

    return {
        **result,
        "filename": filename,
    }