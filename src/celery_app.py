from celery import Celery
from src.config import settings


celery_app = Celery(
    "video_worker",
    broker=f"amqp://{settings.mq_user}:{settings.mq_password}@{settings.mq_host}:{settings.mq_port}/{settings.mq_vhost}",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

import src.videos.tasks
