from sentence_transformers import SentenceTransformer
import subprocess
import tempfile
import os
import numpy as np

_video_model = None

def get_video_model():
    global _video_model
    if _video_model is None:
        print("Loading Qwen3-VL video model (this may take a while on first run)...")
        _video_model = SentenceTransformer("Qwen/Qwen3-VL-Embedding-2B")
    return _video_model


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(result.stdout.strip())


def embed_video_chunks(video_path, chunk_length=120, overlap=30):
    duration = get_video_duration(video_path)
    step = chunk_length - overlap
    model = get_video_model()

    embeddings = []
    start = 0.0
    chunk_idx = 0

    while start < duration:
        end = min(start + chunk_length, duration)
        chunk_duration = end - start

        # extract chunk to a temporary video file for native video embedding
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-ss", str(start),
                    "-t", str(chunk_duration),
                    "-i", video_path,
                    "-c", "copy",
                    "-an",
                    tmp_path,
                ],
                capture_output=True,
                check=True,
            )

            #  Qwen3-VL video embedding
            embedding = model.encode(
                {"video": tmp_path},
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        embeddings.append({
            "id": f"chunk_{chunk_idx}",
            "global_chunk_start": start,
            "global_chunk_end": end,
            "vector": embedding,
        })

        chunk_idx += 1
        start += step

    return embeddings


# if __name__ == "__main__":
#     print(embed_video_chunks("/Users/yashwanth/Desktop/code/Multi Media database/sample.mp4"))