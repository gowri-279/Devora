from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from parser import parse_repository


app = FastAPI(
    title="MentorSpace Repository Parser API",
    description="API for analyzing repositories and returning structured metadata.",
    version="1.0.0"
)


class RepositoryAnalysisRequest(BaseModel):
    repository_url: HttpUrl


@app.get("/")
def root():
    return {
        "service": "MentorSpace Repository Parser",
        "status": "running"
    }


@app.post("/repositories/analyse")
def analyse_repository(request: RepositoryAnalysisRequest):

    try:
        result = parse_repository(str(request.repository_url))

        if result.get("errors"):
            return {
                "status": "completed_with_errors",
                "data": result
            }

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "stage": "repository_analysis",
                "error": str(e)
            }
        )