import os
import cv2
import json
import uuid
import numpy as np
from datetime import datetime, timedelta

from ultralytics import YOLO

from src.database.base_database import BaseDatabase
from .schema import DetectionInput

from loguru import logger
from src.logging.logger_setup import setup_logger

setup_logger(component="detect video")

def detect_video(
    detect_input: DetectionInput,
    db: BaseDatabase
):
    job_id = str(uuid.uuid4())
    logger.info(f"Detection Job: {job_id} started...")

    video_info = db.execute_query("SELECT output_path, created_at FROM video_registry WHERE pk_video_id = %s", (detect_input.video_id, ))
    video_path = video_info[0][0]
    video_start_timestamp = video_info[0][1]

    placeholders = ','.join(['%s'] * len(detect_input.region_ids))
    get_regions_query = f"""
        SELECT pk_region_id, region_name, region_description, polygon 
        FROM region_registry 
        WHERE pk_region_id IN ({placeholders})
    """
    db_region_res = db.execute_query(get_regions_query, tuple(detect_input.region_ids))

    # Format hasilnya seperti ini:
    region_definitions = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "polygon": row[3]  # diasumsikan list of (x, y) seperti [(x1, y1), (x2, y2), ...]
        }
        for row in db_region_res
    ]

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Error reading video file"
    model = YOLO(detect_input.model_name)
    class_names = model.names

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # fallback default

    frame_number = 0
    results_json = []
    video_filename = os.path.basename(video_path)

    # konversi video_start_timestamp ke datetime object
    video_start_dt = video_start_timestamp

    # timestamp job deteksi
    job_timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    output_filename = f"detection_results_{job_id}_{job_timestamp}.json"
    output_path = os.path.join(os.path.dirname(video_path), output_filename)

    # save to detection_jobs table
    insert_deteciton_job_query = """
    INSERT INTO detection_jobs(
        pk_detection_id, fk_video_id, name, description, classes, 
        model_name, tracker, max_frame, output_path, created_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.execute_query(
        insert_deteciton_job_query, (
            job_id, 
            detect_input.video_id, 
            detect_input.name, 
            detect_input.description, 
            detect_input.classes,
            detect_input.model_name,
            detect_input.tracker,
            detect_input.max_frames,
            output_path,
            job_timestamp
        )
    )

    insert_detect_region_mapping_query = """
    INSERT INTO detect_region_mapping(
        fk_region_id,
        fk_detection_id
    ) VALUES (%s, %s)
    """
    for reg in region_definitions:
        db.execute_query(insert_detect_region_mapping_query, (reg['id'], job_id))

    logger.info("Start detecting...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or (detect_input.max_frames > 0 and frame_number >= detect_input.max_frames):
            break

        # timestamp frame sekarang
        current_timestamp = video_start_dt + timedelta(seconds=frame_number / fps)
        timestamp_iso = current_timestamp.isoformat() + "Z"

        result = model.track(
            frame,
            persist=True,
            conf=0.25,
            verbose=False,
            tracker=detect_input.tracker,
            classes=detect_input.classes
        )[0]

        for region in region_definitions:
            frame_objects = []
            count = 0  # inisialisasi counter
            detection_event_id = str(uuid.uuid4())

            boxes = result.boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                cls_name = class_names[cls_id]
                if cls_name not in [class_names[i] for i in detect_input.classes]:
                    continue

                bbox = boxes.xyxy[i].tolist()
                track_id = int(boxes.id[i].item()) if boxes.id is not None else None
                conf = float(boxes.conf[i].item())
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2

                inside = cv2.pointPolygonTest(
                    np.array(region['polygon'], dtype=np.int32),
                    (center_x, center_y),
                    False
                ) >= 0

                if inside:
                    count += 1

                frame_objects.append({
                    "id": track_id,
                    "bbox": [int(v) for v in bbox],
                    "class": cls_name,
                    "confidence": conf,
                    "inside_region": inside
                })

            # masukkan detection event disini
            query_insert_detection_event = """
            INSERT INTO detection_event(
                pk_detection_event_id,
                fk_detection_id,
                fk_region_id,
                frame_number,
                timestamp,
                count
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(
                query_insert_detection_event,
                (
                    detection_event_id,
                    job_id,
                    region['id'],
                    frame_number,
                    timestamp_iso,
                    count
                )
            )

            # masukkan detection objects kesini
            insert_query = """
                INSERT INTO detection_objects (
                    pk_object_id,
                    fk_detection_event_id,
                    tracker_id,
                    bbox,
                    confidence,
                    inside_region
                ) VALUES %s
            """

            params_list = [
                (
                    str(uuid.uuid4()),
                    detection_event_id,
                    obj["id"],
                    obj["bbox"],
                    obj["confidence"],
                    obj["inside_region"]
                )
                for obj in frame_objects
            ]

            db.execute_many(insert_query, params_list)


            results_json.append({
                "video_id": detect_input.video_id,
                "video_filename": video_path,
                "frame_number": frame_number,
                "timestamp": timestamp_iso,
                "region_id": region['id'],
                "region_name": region['name'],
                "region_description": region['description'],
                "region_polygon": region['polygon'],
                "objects": frame_objects,
                "count": count
            })

        frame_number += 1

    cap.release()

    with open(output_path, "w") as f:
        json.dump(results_json, f, indent=2)
        
    logger.info(f"Detection job: {job_id} finished, json saved to: {output_path}")

    return results_json


# # Contoh UUID dari database Anda
# VIDEO_ID = "750775f1-6962-4388-9c13-e6d5f2c2c327"
# REGION_IDS = [
#     "e8621cf4-2dfc-46b7-8d9b-0cb025a0967b",
#     "11a0bb15-a7dd-494e-b776-55ee914f91e8"
# ]

# detection_input = DetectionInput(
#     name="Deteksi Orang di Halte 3",
#     description="Uji coba deteksi orang dengan YOLO11 dan BotSort",
#     video_id=VIDEO_ID,
#     region_ids=REGION_IDS,
#     model_name="yolov8n.pt",
#     tracker="botsort.yaml",
#     classes=[0],  # hanya 'person'
#     max_frames=-1,
#     save=True
# )

# results = detect_video(detection_input, get_database_instance())
# print(f"Jumlah hasil deteksi: {len(results)}")
# print("Contoh hasil deteksi pertama:")
# if results:
#     from pprint import pprint
#     pprint(results[0])
