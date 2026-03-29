from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.schemas import UserRead, UserPut
from src.users.service import (
    get_users, 
    set_avatar,
    update_user
)
from src.users.models import User
from src.auth.jwt_service import authorize


router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)):
    return await get_users(db)

@router.get("/me", response_model=UserRead)
async def profile(user: User = Depends(authorize)):
    return user

@router.put("/me/update", response_model=UserRead)
async def update_me(
    data: UserPut,
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db),
):
    return await update_user(user, data, db)

@router.post("/upload_avatar")
async def upload_avatar(
    upload_file: UploadFile,
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db)
):
    return await set_avatar(user, upload_file, db)
