from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from typing import List, Optional

from src.database.base_database import BaseDatabase
from src.database.database_factory import get_database_instance
from src.detect.detect_video import detect_video
from .schema import DetectionJobOut, DetectionEventOut, DetectionInput, DetectionObjectOut

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


@router.get("/detection_jobs", response_model=List[DetectionJobOut])
def get_detection_jobs(
    db: BaseDatabase = Depends(get_database_instance),
    video_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    base_query = """
    SELECT
        pk_detection_id,
        fk_video_id,
        name,
        description,
        classes,
        model_name,
        tracker,
        max_frame,
        output_path,
        created_at
    FROM detection_jobs
    """
    filters = []
    params = []

    if video_id:
        filters.append("fk_video_id = %s")
        params.append(str(video_id))

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    rows = db.execute_query(base_query, tuple(params))
    return [
        DetectionJobOut(
            pk_detection_id=row[0],
            fk_video_id=row[1],
            name=row[2],
            description=row[3],
            classes=row[4],
            model_name=row[5],
            tracker=row[6],
            max_frame=row[7],
            output_path=row[8],
            created_at=row[9].isoformat() if hasattr(row[9], 'isoformat') else str(row[9])
        )
        for row in rows
    ]


@router.get("/detection_events", response_model=List[DetectionEventOut])
def get_detection_events(
    db: BaseDatabase = Depends(get_database_instance),
    detection_id: Optional[UUID] = Query(None),
    region_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = """
    SELECT
        pk_detection_event_id,
        fk_detection_id,
        fk_region_id,
        frame_number,
        timestamp,
        count,
        created_at
    FROM detection_event
    """
    filters = []
    params = []

    if detection_id:
        filters.append("fk_detection_id = %s")
        params.append(str(detection_id))

    if region_id:
        filters.append("fk_region_id = %s")
        params.append(str(region_id))

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY frame_number ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))

    return [
        DetectionEventOut(
            pk_detection_event_id=row[0],
            fk_detection_id=row[1],
            fk_region_id=row[2],
            frame_number=row[3],
            timestamp=row[4],
            count=row[5],
            created_at=row[6]
        )
        for row in rows
    ]


@router.get("/detection_objects", response_model=List[DetectionObjectOut])
def get_detection_objects(
    db: BaseDatabase = Depends(get_database_instance),
    detection_event_id: Optional[UUID] = Query(None),
    inside_region: Optional[bool] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = """
    SELECT
        pk_object_id,
        fk_detection_event_id,
        tracker_id,
        bbox,
        confidence,
        inside_region,
        created_at
    FROM detection_objects
    """
    filters = []
    params = []

    if detection_event_id:
        filters.append("fk_detection_event_id = %s")
        params.append(str(detection_event_id))

    if inside_region is not None:
        filters.append("inside_region = %s")
        params.append(inside_region)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY created_at ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))

    return [
        DetectionObjectOut(
            pk_object_id=row[0],
            fk_detection_event_id=row[1],
            tracker_id=row[2],
            bbox=row[3],
            confidence=row[4],
            inside_region=row[5],
            created_at=row[6]
        )
        for row in rows
    ]