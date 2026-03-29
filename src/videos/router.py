from fastapi import (
    APIRouter, UploadFile, Depends, BackgroundTasks
)
from src.auth.jwt_service import authorize
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.models import User
from src.videos.service import (
    set_video, 
    get_video_service,
    get_my_videos_service,
    get_all_videos_service,
    get_hls_file,
)
from src.videos.schemas import VideoRead


router = APIRouter()
    
@router.post("/add", response_model=VideoRead)
async def upload_video(
    upload_file: UploadFile,
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db),
):
    return await set_video(user, upload_file, db)

@router.get("/my", response_model=list[VideoRead])
async def get_my_videos(
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db)
):
    return await get_my_videos_service(user, db)

@router.get(
    "/all", response_model=list[VideoRead], description="Only for admins."
)
async def get_all_videos(
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_videos_service(user, db)

@router.get("/{video_id}")
async def get_video(
    video_id: int,
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db),
):
    return await get_video_service(video_id, user, db)

@router.get("/hls/{video_uuid}/{filename}")
async def serve_hls_file(
    video_uuid: str,
    filename: str,
    user: User = Depends(authorize),
    db: AsyncSession = Depends(get_db),
):
    return await get_hls_file(
        video_uuid, filename, user, db
    )
