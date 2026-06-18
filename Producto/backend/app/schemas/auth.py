from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def _password_complexity(cls, value: str) -> str:
        """Exige al menos una letra y un número (OWASP A07: autenticación robusta)."""
        if not any(c.isalpha() for c in value):
            raise ValueError("La contraseña debe contener al menos una letra.")
        if not any(c.isdigit() for c in value):
            raise ValueError("La contraseña debe contener al menos un número.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserInfo(BaseModel):
    user_id: str
    username: str
    email: str
