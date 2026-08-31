from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "developer"


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest):
    return {
        "message": "Registration successful",
        "access_token": f"mock-token-{data.email}",
        "user": {
            "name": data.name,
            "email": data.email,
            "role": data.role
        }
    }


@router.post("/login")
def login(data: LoginRequest):
    return {
        "message": "Login successful",
        "access_token": f"mock-token-{data.email}",
        "user": {
            "email": data.email
        }
    }