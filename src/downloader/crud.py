import os
import shutil
from typing import List

from src.database.postgres_database import PostgresDatabase
from .schema import VideoFilter

def get_videos(db: PostgresDatabase, filters: VideoFilter) -> List[tuple]:
    base_query = "SELECT * FROM video_registry WHERE 1=1"
    params = []

    if filters.name:
        base_query += " AND name ILIKE %s"
        params.append(f"%{filters.name}%")

    if filters.description:
        base_query += " AND description ILIKE %s"
        params.append(f"%{filters.description}%")

    if filters.min_duration is not None:
        base_query += " AND duration >= %s"
        params.append(filters.min_duration)

    if filters.max_duration is not None:
        base_query += " AND duration <= %s"
        params.append(filters.max_duration)

    if filters.created_after:
        base_query += " AND created_at >= %s"
        params.append(filters.created_after)

    if filters.created_before:
        base_query += " AND created_at <= %s"
        params.append(filters.created_before)

    base_query += " ORDER BY created_at DESC"
    return db.execute_query(base_query, tuple(params))


def delete_video_and_file(db: PostgresDatabase, video_id: str) -> dict:
    # Ambil path dari video yang ingin dihapus
    select_query = "SELECT output_folder FROM video_registry WHERE pk_video_id = %s"
    rows = db.execute_query(select_query, (video_id,))
    
    if not rows:
        return {"deleted": False, "reason": "not_found"}

    row = rows[0]

    output_folder = row[0]

    # Hapus folder dari sistem
    try:
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder)
    except Exception as e:
        return {"deleted": False, "reason": f"folder_delete_error: {str(e)}"}

    # Hapus data dari database
    delete_query = "DELETE FROM video_registry WHERE pk_video_id = %s"
    db.execute_query(delete_query, (video_id,))

    return {"deleted": True, "output_folder": output_folder}