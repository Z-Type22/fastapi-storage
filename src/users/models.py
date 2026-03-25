from src.database import Base
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as ModelEnum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(ModelEnum(UserRole), nullable=False, default=UserRole.USER)
    avatar = Column(String, nullable=True)
