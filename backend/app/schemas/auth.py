from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str = Field(min_length=20)


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
