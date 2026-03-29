from src.database import Base
from sqlalchemy.sql import func
from enum import Enum
from sqlalchemy import (
    Column, 
    DateTime, 
    Integer, 
    String, 
    ForeignKey,
    Enum as ModelEnum,
)
from sqlalchemy.orm import relationship
from src.users.models import User
import uuid


class Video(Base):

    class Status(str, Enum):
        UPLOADED = "uploaded"
        PROCESSING = "processing"
        READY = "ready"
        FAILED = "failed"

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(
        String,
        unique=True,
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user = relationship(
        User,
        foreign_keys=[user_id],
        backref="video_users"
    )
    source_path = Column(String, nullable=False)
    hls_path = Column(String, nullable=True)
    status = Column(ModelEnum(Status), nullable=False, default=Status.UPLOADED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
