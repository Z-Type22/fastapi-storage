from pydantic import BaseModel, EmailStr
from src.users.models import UserRole


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    username: str
    avatar: str | None = None
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class UserPut(BaseModel):
    email: EmailStr
    username: str
