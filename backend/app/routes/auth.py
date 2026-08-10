from fastapi import APIRouter

router = APIRouter(tags=["Authentication"])


@router.post("/register")
def register():
    return {
        "message": "Register endpoint is working!"
    }


@router.post("/login")
def login():
    return {
        "message": "Login endpoint is working!"
    }