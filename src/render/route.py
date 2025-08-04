# file: src/api/render.py

from fastapi import APIRouter, Depends, HTTPException
from .schema import RenderResponse
from src.database.base_database import BaseDatabase
from src.database.database_factory import get_database_instance
from src.render.render_detection import render_region_counter_output
from loguru import logger

router = APIRouter(prefix="/render", tags=["Render"])

def get_db():
    return get_database_instance()

@router.post("/{detection_id}", response_model=RenderResponse)
def render_video(detection_id: str, db: BaseDatabase = Depends(get_db)):
    try:
        render_id, output_path = render_region_counter_output(detection_id, db)
        return RenderResponse(render_id=render_id, output_path=output_path)
    except Exception as e:
        logger.exception("Failed to render video")
        raise HTTPException(status_code=500, detail=str(e))
