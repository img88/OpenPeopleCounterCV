from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.database.database_factory import get_database_instance
from src.detect.detect_video import DetectionInput, detect_video

import traceback

router = APIRouter(prefix="/detection", tags=["Detection"])

@router.post("/", summary="Run detection job on video")
async def run_detection(input_data: DetectionInput):
    """
    ```
    {
    "name": "Coba deteksi orang",
    "description": "Coba deteksi pakai yolo11n.pt botsort",
    "video_id": "036400d8-eb12-4751-acc0-ee1de4a7367d",
    "region_ids": [
        "11a0bb15-a7dd-494e-b776-55ee914f91e8", "e8621cf4-2dfc-46b7-8d9b-0cb025a0967b"
    ],
    "model_name": "yolo11n.pt",
    "tracker": "botsort.yaml",
    "classes": [
        0
    ],
    "max_frames": -1,
    "save": true
    }
    ```
    """
    try:
        db = get_database_instance()
        result = detect_video(input_data, db)
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Detection completed. Total frames processed: {len(result)}",
                "output_count": len(result),
                "sample_result": result[0] if result else None
            }
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
