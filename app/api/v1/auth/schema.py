from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Literal

Role = Literal["user", "editor", "admin"]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    model_config = ConfigDict(
        from_attributes=True
    )  # para que tambien recibe objetos ORM


class UserPublic(UserBase):
    # username:str
    id: int
    role: Role
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=6, max_length=72
    )  # Para create si es necesario validar el tamano del password
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class RoleUpdate(BaseModel):
    role: Role


class TokenData(BaseModel):
    sub: str
    username: str
