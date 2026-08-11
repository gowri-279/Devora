from pydantic import BaseModel
from typing import List
from app.ingest_core import run_ingest


class IngestRequest(BaseModel):
    project_id: str
    file_paths: List[str]
    is_new_project: bool = True  # False if just adding docs to the currently active project


def ingest_files(req: IngestRequest):
    return run_ingest(req.project_id, req.file_paths, is_new_project=req.is_new_project)
