from src.videos.models import Video
from src.videos.hls import convert_to_hls
from src.database import AsyncSessionLocal
from src.celery_app import celery_app
from pathlib import Path
import asyncio


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def process_video_task(self, video_id: int, input_path: str, output_dir: str):
    asyncio.run(_process_video(video_id, Path(input_path), Path(output_dir)))


async def _process_video(
    video_id: int, input_path: Path, output_dir: Path
):
    async with AsyncSessionLocal() as db: 
        video = await db.get(Video, video_id)

        try:
            await convert_to_hls(input_path, output_dir)
            video.hls_path = str(output_dir / "index.m3u8")
            video.status = Video.Status.READY
        except Exception as e:
            video.status = Video.Status.FAILED

        await db.commit()
