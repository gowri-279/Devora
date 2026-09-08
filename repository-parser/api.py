import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from parser import parse_repository


app = FastAPI(
    title="DEVORA Repository Parser API",
    description="API for analyzing repositories and returning structured metadata.",
    version="1.0.0",
)


class RepositoryAnalysisRequest(BaseModel):
    repository_url: HttpUrl


ARTIFACTS: dict[str, str] = {}


@app.get("/")
def root():
    return {
        "service": "DEVORA Repository Parser",
        "status": "running",
    }


@app.post("/repositories/analyse")
def analyse_repository(request: RepositoryAnalysisRequest):
    try:
        result = parse_repository(str(request.repository_url))

        if result.get("errors"):
            return {
                "status": "completed_with_errors",
                "data": result,
            }

        source_artifact = result.get("source_artifact")

        if source_artifact:
            artifact_path = Path(source_artifact["path"])

            if not artifact_path.exists():
                raise FileNotFoundError(
                    "Generated source artifact could not be found."
                )

            artifact_id = uuid.uuid4().hex
            ARTIFACTS[artifact_id] = str(artifact_path)

            parser_base_url = os.getenv("PARSER_BASE_URL", "").rstrip("/")

            artifact_url = f"/artifacts/{artifact_id}"

            if parser_base_url:
                artifact_url = f"{parser_base_url}{artifact_url}"

            result["source_artifact"] = {
                "type": source_artifact["type"],
                "format": source_artifact["format"],
                "url": artifact_url,
            }

        return {
            "status": "success",
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "stage": "repository_analysis",
                "error": str(e),
            },
        )


@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str):
    artifact_path = ARTIFACTS.get(artifact_id)

    if not artifact_path:
        raise HTTPException(
            status_code=404,
            detail="Source artifact not found.",
        )

    path = Path(artifact_path)

    if not path.exists():
        ARTIFACTS.pop(artifact_id, None)
        raise HTTPException(
            status_code=404,
            detail="Source artifact is no longer available.",
        )

    return FileResponse(
        path=path,
        media_type="application/zip",
        filename="repository_source.zip",
    )