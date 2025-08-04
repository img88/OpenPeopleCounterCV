from pydantic import BaseModel
from typing import Any
from uuid import UUID
from datetime import datetime

class RegionCreate(BaseModel):
    region_name: str
    region_description: str
    polygon: Any  # gunakan List[List[int]] jika ingin lebih ketat

class RegionUpdate(BaseModel):
    region_name: str
    region_description: str
    polygon: Any

class RegionOut(BaseModel):
    pk_region_id: UUID
    region_name: str
    region_description: str
    polygon: Any
    created_at: datetime
    updated_at: datetime
