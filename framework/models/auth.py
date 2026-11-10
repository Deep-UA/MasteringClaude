from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str = Field(repr=False)  # kept out of tracebacks


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
