import uuid

from sqlmodel import Field, SQLModel


class LoginResponse(SQLModel):
    access_token: str = Field(min_length=1)
    token_type: str = "bearer"  # noqa: S105


class JWTPayload(SQLModel):
    user_id: uuid.UUID
    role: str
    iat: int  # Issued at time as a Unix timestamp
    exp: int  # Expiration time as a Unix timestamp
    jti: uuid.UUID  # JWT ID (unique identifier for the token)


class JWTBlacklist(SQLModel, table=True):
    __tablename__ = "jwt_blacklist"
    jti: uuid.UUID = Field(primary_key=True)  # JWT ID
    iat: int = Field(nullable=False)  # Issued at time as a Unix timestamp
    exp: int = Field(nullable=False)  # Expiration time as a Unix timestamp


class UserChangePasswordResponse(SQLModel):
    message: str = "Password changed successfully."
