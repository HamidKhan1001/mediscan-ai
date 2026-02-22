"""Auth endpoints — login, register, token refresh"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.core.security import create_access_token, hash_password, verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# In production, replace with a real database
DEMO_USERS = {
    "demo@mediscan.ai": {
        "hashed_password": hash_password("demo1234"),
        "role": "clinician",
        "user_id": "demo-user-001",
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = DEMO_USERS.get(body.email)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user["user_id"],
        "email": body.email,
        "role": user["role"],
    })
    return TokenResponse(access_token=token)
