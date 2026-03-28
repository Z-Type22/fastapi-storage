from src.videos.models import Video
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import asyncio


async def convert_to_hls(
    input_path: Path,
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    playlist = output_dir / "index.m3u8"

    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i", str(input_path),
        "-profile:v", "baseline",
        "-level", "3.0",
        "-start_number", "0",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-f", "hls",
        str(playlist),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

async def process_video_task(
    video_id: int, input_path: Path, 
    output_dir: Path, db: AsyncSession
):

    video = await db.get(Video, video_id)

    try:
        await convert_to_hls(input_path, output_dir)
        video.hls_path = str(output_dir / "index.m3u8")
        video.status = Video.Status.READY
    except Exception as e:
        video.status = Video.Status.FAILED

    await db.commit()
