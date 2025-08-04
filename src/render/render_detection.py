import json
import cv2
import numpy as np
from collections import defaultdict
import os

def render_region_counter_output(
    detection_id
):
    # Load JSON data dan filter sesuai video_id
    with open(json_path, "r") as f:
        data = json.load(f)

    data_by_frame = defaultdict(list)
    for item in data:
        if item['video_id'] == video_id:
            data_by_frame[item['frame_number']].append(item)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Buat output path berdasarkan video_path
    base_folder = os.path.dirname(video_path)
    filename = os.path.splitext(os.path.basename(video_path))[0]
    ext = os.path.splitext(video_path)[1]
    json_filename = os.path.basename(json_path).split(".")[0]
    output_path = os.path.join(base_folder, f"{filename}_rendered_{json_filename}_{ext}")

    writer = None
    if save:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    frame_num = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_num in data_by_frame:
            for ir, region in enumerate(data_by_frame[frame_num]):
                # Gambar polygon region
                pts = np.array(region["region_polygon"], dtype=np.int32)
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=2)
                
                M = pts.mean(axis=0)
                center_x, center_y = int(M[0]), int(M[1])

                # Tampilkan teks di tengah polygon
                text = f"{region['region_name']}, count: {region['count']}"
                cv2.putText(frame, text, (center_x, center_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                for obj in region["objects"]:
                    bbox = obj["bbox"]
                    obj_id = obj.get("id", None)
                    class_name = obj["class"]
                    inside = obj["inside_region"]
                    color = (0, 255, 0) if inside else (0, 0, 255)

                    # Gambar bbox
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

                    # Tulis info objek
                    label = f"{class_name}#{obj_id}" if obj_id is not None else class_name
                    label += f" {region['region_name']}"
                    label += " IN" if inside else " OUT"
                    space = (ir + 1) * 15
                    cv2.putText(frame, label, (bbox[0], bbox[1] - space),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if show:
            cv2.imshow("Rendered Region Counter", frame)
            if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
                break

        if save:
            writer.write(frame)

        frame_num += 1

    cap.release()
    if writer:
        writer.release()
    if show:
        cv2.destroyAllWindows()

    print(f"[INFO] Output disimpan di: {output_path}")