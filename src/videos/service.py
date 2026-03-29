from src.users.models import User
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from src.videos.models import Video
from src.users.models import UserRole
from src.videos.tasks import process_video_task
from sqlalchemy import select
from src.config import settings
from pathlib import Path
import shutil
import uuid


async def set_video(
    user: User, 
    upload_file: UploadFile, 
    db: AsyncSession,
):
    VIDEO_DIR = settings.video_dir
    HLS_DIR = settings.hls_dir

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    HLS_DIR.mkdir(parents=True, exist_ok=True)

    if Path(upload_file.filename).suffix.lower() != ".mp4":
        raise HTTPException(
            status_code=400,
            detail="Only .mp4 files are allowed"
        )
    
    ALLOWED_MP4_MIME_TYPES = {
        "video/mp4",
        "application/mp4",
        "video/mpeg4",
    }

    if upload_file.content_type not in ALLOWED_MP4_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid video MIME type"
        )

    video_uuid = uuid.uuid4()
    filename = f"{video_uuid}.mp4"
    file_path = VIDEO_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

    video_obj = Video(
        user_id=user.id,
        source_path=settings.video_dir_prefix + filename,
        status=Video.Status.PROCESSING,
        uuid=str(video_uuid)
    )

    db.add(video_obj)
    await db.commit()
    await db.refresh(video_obj)

    hls_output_dir = HLS_DIR / str(video_uuid)

    process_video_task.delay(
        video_obj.id,
        str(file_path),
        str(hls_output_dir),
    )

    return video_obj

async def get_video_service(
    video_id: int, user: User, db: AsyncSession,
):
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video_obj = result.scalar_one_or_none()
    if video_obj and (user.id == video_obj.user_id or user.role == UserRole.ADMIN):
        return {"hls_url": video_obj.hls_path}
    
    raise HTTPException(status_code=404, detail="File not found.")

async def get_hls_file(
    video_uuid: str, filename: str, 
    user: User, db: AsyncSession
):
    result = await db.execute(
        select(Video).where(Video.uuid == video_uuid)
    )
    video_obj = result.scalar_one_or_none()
    if video_obj:
        file_path = settings.hls_dir / str(video_uuid) / filename
        if file_path and (user.id == video_obj.user_id or user.role == UserRole.ADMIN):
            media_type = (
                "application/vnd.apple.mpegurl"
                if filename.endswith(".m3u8")
                else "video/MP2T"
            )

            return FileResponse(file_path, media_type=media_type)
    
    raise HTTPException(status_code=404, detail="Video not found.")

async def get_my_videos_service(
    user: User, db: AsyncSession
):
    result = await db.execute(select(Video).where(Video.user_id == user.id))
    return result.scalars().all()

async def get_all_videos_service(
    user: User, db: AsyncSession
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Forbidden."
        )

    result = await db.execute(select(Video))
    return result.scalars().all()
