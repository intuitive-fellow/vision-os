from pydantic import EmailStr, Field, field_validator

from apps.base.schemas import BaseInputSchema


class SendOTPSchema(BaseInputSchema):
    """Validate the email address for OTP dispatch."""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class VerifyOTPSchema(BaseInputSchema):
    """Validate email + OTP code pair for authentication."""

    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("code")
    @classmethod
    def digits_only(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("OTP must contain digits only.")
        return v


class TokenRefreshSchema(BaseInputSchema):
    """Validate a JWT refresh token for rotation."""

    refresh: str


class LogoutSchema(BaseInputSchema):
    """Validate a JWT refresh token for blacklisting."""

    refresh: str
