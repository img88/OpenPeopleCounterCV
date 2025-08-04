from pydantic import BaseModel


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