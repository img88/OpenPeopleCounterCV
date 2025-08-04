from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class VideoInput(BaseModel):
    name: str
    description: str
    url: str
    duration: int
    output_folder: str = "downloaded_video"

class VideoOut(BaseModel):
    pk_video_id: UUID
    name: str
    description: Optional[str]
    url: str
    duration: int
    output_folder: str
    output_path: str
    created_at: datetime

class VideoFilter(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
