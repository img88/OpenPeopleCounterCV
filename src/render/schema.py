from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RenderResponse(BaseModel):
    render_id: str
    output_path: str


class RenderRegistryOut(BaseModel):
    pk_render_id: UUID
    fk_detection_id: UUID
    video_path: str
    created_at: datetime