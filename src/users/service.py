from sqlalchemy.ext.asyncio import AsyncSession
from src.users import models
from sqlalchemy import select
from fastapi import UploadFile, HTTPException
from src.users.models import User
from src.users.schemas import UserPut
from src.config import settings
import shutil


async def get_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    return result.scalars().all()

async def set_avatar(
    user: User, upload_file: UploadFile, db: AsyncSession
):    
    AVATAR_DIR = settings.avatar_dir
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{user.id}_{upload_file.filename}"
    file_path = AVATAR_DIR / filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

    if user.avatar:
        old_filename = user.avatar.replace(
            settings.avatar_dir_prefix, ""
        )
        old_file_path = AVATAR_DIR / old_filename

        if old_file_path.exists() and old_file_path.is_file():
            old_file_path.unlink()

    user.avatar = settings.avatar_dir_prefix + filename

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"detail": "Success."}

async def update_user(user: User, data: UserPut, db: AsyncSession):
    if data.email != user.email:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

    if data.username != user.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")

    user.email = data.email
    user.username = data.username

    await db.commit()
    await db.refresh(user)

    return user
