from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class DetectionObjectOut(BaseModel):
    pk_object_id: UUID
    fk_detection_event_id: UUID
    tracker_id: int
    bbox: List[int]
    confidence: float
    inside_region: bool
    created_at: datetime
    

class DetectionEventOut(BaseModel):
    pk_detection_event_id: UUID
    fk_detection_id: UUID
    fk_region_id: UUID
    frame_number: int
    timestamp: datetime
    count: int
    created_at: datetime


class DetectionInput(BaseModel):
    name: str
    description: str
    video_id: str
    region_ids: list[str]
    model_name: str = "yolo11n.pt"
    tracker: str = "botsort.yaml"
    classes: list[int] = [0]
    max_frames: int = -1
    save: bool = True


class DetectionJobOut(BaseModel):
    pk_detection_id: UUID
    fk_video_id: UUID
    name: str
    description: str
    classes: List[int]
    model_name: str
    tracker: str
    max_frame: int
    output_path: str
    created_at: str