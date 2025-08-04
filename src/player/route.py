from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
import os

from src.database.database_factory import get_database_instance
from src.database.base_database import BaseDatabase
from src.logging.logger_setup import setup_logger
from loguru import logger

setup_logger(component="Video Player")

from .video_player import iter_video_stream

router = APIRouter(prefix="/videos", tags=["Videos"])

def get_db():
    return get_database_instance()

@router.get("/player")
def play_video(detection_id: str = Query(..., description="Detection id"), db: BaseDatabase = Depends(get_db)):
    get_video_path_query = """SELECT video_path FROM render_registry WHERE fk_detection_id = %s"""
    path = db.execute_query(get_video_path_query, (detection_id,))[0][0]
    logger.info(f"Play video from detection id: {detection_id}, video_path: {path}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found")

    return StreamingResponse(iter_video_stream(path), media_type="video/avi")
