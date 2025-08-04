import os
import uuid
import json
import subprocess
from datetime import datetime

from .schema import VideoInput

from src.database.base_database import BaseDatabase
from src.database.database_factory import get_database_instance

from src.logging.logger_setup import setup_logger
from loguru import logger

setup_logger("video_downloader")


def download_video(video_input: VideoInput):
    """
    Menyimpan video stream dari URL (.m3u8) selama durasi tertentu ke output_folder/name
    dan menyimpan metadata dalam format JSON.
    """
    video_id = str(uuid.uuid4())
    output_dir = os.path.join(video_input.output_folder, video_id)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{video_input.name}_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-i', video_input.url,
        '-t', str(video_input.duration),
        '-c', 'copy',
        output_path
    ]

    logger.debug(' '.join(ffmpeg_cmd))

    try:
        logger.info(f"Saving stream to {output_path} for {video_input.duration} seconds...")
        subprocess.run(ffmpeg_cmd, check=True)
        logger.info(f"Video saved: {output_path}")

        metadata = {
            "id": video_id,
            "name": video_input.name,
            "description": video_input.description,
            "url": video_input.url,
            "duration": video_input.duration,
            "created_at": datetime.now().isoformat(),
            "video_path": output_path
        }

        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to {metadata_path}")

        db = get_database_instance()

        video_id = insert_video_metadata(
            db=db,
            id=video_id,
            name=video_input.name,
            description=video_input.description,
            url=video_input.url,
            duration=video_input.duration,
            output_folder=output_dir,
            output_path=output_path
        )

        return {"status": "success", "video_id": video_id, "video_path": output_path, "metadata_path": metadata_path}
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Gagal menyimpan stream: {e}")
        return {"status": "error", "message": str(e)}


def insert_video_metadata(
    db: BaseDatabase,
    id: str,
    name: str,
    description: str,
    url: str,
    duration: int,
    output_folder: str,
    output_path: str,
    created_at: datetime = None
):
    created_at = created_at or datetime.now()

    query = """
    INSERT INTO video_registry (
        pk_video_id, name, description, url, duration,
        output_folder, output_path, created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        str(id),
        name,
        description,
        url,
        duration,
        output_folder,
        output_path,
        created_at
    )

    db.execute_query(query, params)
    return str(id)
