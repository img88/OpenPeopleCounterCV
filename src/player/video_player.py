def iter_video_stream(video_path: str, chunk_size: int = 1024 * 1024):
    """
    Generator untuk membaca video dalam potongan kecil.
    """
    try:
        with open(video_path, mode="rb") as file:
            while chunk := file.read(chunk_size):
                yield chunk
    except Exception as e:
        raise RuntimeError(f"Error reading video: {e}")
