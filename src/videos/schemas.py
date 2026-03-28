from pydantic import BaseModel
from datetime import datetime
from src.users.schemas import UserRead
from src.videos.models import Video


class VideoRead(BaseModel):
    id: int
    source_path: str
    status: Video.Status
    created_at: datetime
    user: UserRead
    
    model_config = {
        "from_attributes": True
    }
