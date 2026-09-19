from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.services.knowledge_engine import get_developer_twin, create_developer_twin, upload_developer_profile


router = APIRouter(
    prefix="/api",
    tags=["Developer Twin"],
)


@router.get("/developer-twin/{developer_id}")
def get_twin(
    developer_id: str,
    project_id: str,
):
    try:
        return get_developer_twin(
            developer_id=developer_id,
            project_id=project_id,
        )

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Developer Twin unavailable: {error}",
        ) from error

@router.post("/developer-twin/from-resume")
async def create_twin_from_resume(
    developer_id: str = Form(...),
    project_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        content = await file.read()

        profile = upload_developer_profile(
            file_bytes=content,
            filename=file.filename or "skill-profile.pdf",
        )

        twin = create_developer_twin(
            developer_id=developer_id,
            project_id=project_id,
            skills=profile.get("skills", {}),
        )

        return {
            "status": "success",
            "profile": profile,
            "developer_twin": twin.get(
                "developer_twin",
                twin,
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not create Developer Twin from profile: {error}",
        ) from error
