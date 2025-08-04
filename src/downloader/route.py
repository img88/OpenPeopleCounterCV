from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from . import crud as crud_video
from .schema import VideoOut, VideoFilter
from .download_video import VideoInput, download_video

from src.database.database_factory import get_database_instance
from src.database.base_database import BaseDatabase

router = APIRouter(prefix="/videos", tags=["Videos"])

def get_db():
    return get_database_instance()

@router.post("/download")
async def download_video_route(video_input: VideoInput):
    """
    ```
    {
    "name": "kepatihan",
    "description": "CCTV Malioboro - Kepatihan",
    "url": "https://cctvjss.jogjakota.go.id/malioboro/Malioboro_10_Kepatihan.stream/playlist.m3u8",
    "duration": 30,
    "output_folder": "downloaded_video"
    }
    ```
    """
    result = download_video(video_input)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return {
        "message": "Video berhasil disimpan",
        "video_id": result["video_id"],
        "video_path": result["video_path"],
        "metadata_path": result["metadata_path"]
    }


@router.get("/", response_model=List[VideoOut])
def list_videos(
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    min_duration: Optional[int] = Query(None),
    max_duration: Optional[int] = Query(None),
    created_after: Optional[str] = Query(None),
    created_before: Optional[str] = Query(None),
    db: BaseDatabase = Depends(get_db)
):
    filters = VideoFilter(
        name=name,
        description=description,
        min_duration=min_duration,
        max_duration=max_duration,
        created_after=created_after,
        created_before=created_before
    )
    rows = crud_video.get_videos(db, filters)

    return [VideoOut(**dict(zip([
        "pk_video_id", "name", "description", "url",
        "duration", "output_folder", "output_path", "created_at"
    ], row))) for row in rows]


@router.delete("/{video_id}")
def delete_video(video_id: UUID, db: BaseDatabase = Depends(get_db)):
    result = crud_video.delete_video_and_file(db, str(video_id))

    if not result["deleted"]:
        if result.get("reason") == "not_found":
            raise HTTPException(status_code=404, detail="Video not found")
        elif "folder_delete_error" in result.get("reason", ""):
            raise HTTPException(status_code=500, detail=f"Database deleted, but failed to delete folder: {result['reason']}")

    return {
        "message": "Video and folder deleted successfully",
        "output_folder": result["output_folder"]
    }
