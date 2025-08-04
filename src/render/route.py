from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from .schema import RenderResponse, RenderRegistryOut
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

@router.get("/render_registry", response_model=List[RenderRegistryOut])
def list_render_registry(
    db: BaseDatabase = Depends(get_database_instance),
    detection_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    query = """
    SELECT
        pk_render_id,
        fk_detection_id,
        video_path,
        created_at
    FROM render_registry
    """
    filters = []
    params = []

    if detection_id:
        filters.append("fk_detection_id = %s")
        params.append(str(detection_id))

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    rows = db.execute_query(query, tuple(params))

    return [
        RenderRegistryOut(
            pk_render_id=row[0],
            fk_detection_id=row[1],
            video_path=row[2],
            created_at=row[3]
        )
        for row in rows
    ]