import sys
import os
import subprocess

def check_imports():
    print("=" * 60)
    print("[*] MMDB Project Pre-run Diagnostics")
    print("=" * 60)
    
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "celery": "Celery",
        "redis": "Redis",
        "lancedb": "LanceDB",
        "pydantic": "Pydantic",
        "streamlit": "Streamlit",
        "fitz": "PyMuPDF (fitz)",
        "faster_whisper": "Faster-Whisper",
        "torch": "PyTorch",
        "librosa": "Librosa",
        "transformers": "Hugging Face Transformers",
        "sentence_transformers": "Sentence Transformers",
        "PIL": "Pillow (PIL)",
        "paddleocr": "PaddleOCR",
        "paddle": "PaddlePaddle",
        "numpy": "NumPy",
        "spacy": "spaCy",
        "rank_bm25": "Rank-BM25",
        "rapidfuzz": "RapidFuzz"
    }
    
    missing = []
    print("\nChecking Python packages:")
    for lib, name in dependencies.items():
        try:
            __import__(lib)
            print(f"  [OK] {name} is installed")
        except ImportError:
            print(f"  [X] {name} is missing")
            missing.append(lib)
            
    # Check spaCy model
    if "spacy" not in missing:
        try:
            import spacy
            spacy.load("en_core_web_sm")
            print("  [OK] spaCy English model (en_core_web_sm) is installed.")
        except Exception:
            print("  [X] spaCy English model (en_core_web_sm) is missing.")
            print("      Please run: python -m spacy download en_core_web_sm")
            
    if missing:
        print(f"\nMissing libraries: {', '.join(missing)}")
        print("Please install them using: pip install -r requirements.txt")
    else:
        print("\nAll libraries are successfully installed!")

    # Check FFmpeg
    print("\nChecking FFmpeg (system dependency for audio/video processing):")
    try:
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print("  [OK] FFmpeg is installed and accessible.")
    except Exception:
        print("  [X] FFmpeg is not found in your PATH.")
        print("      Ensure FFmpeg is installed and added to your system Environment Variables.")

    print("\nChecking Redis (optional - if running with Celery worker):")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
        r.ping()
        print("  [OK] Local Redis server is running.")
    except Exception:
        print("  [INFO] Local Redis is not running. (Application will automatically use Celery Eager Mode)")

    print("=" * 60)

if __name__ == "__main__":
    # Ensure stdout is forced to utf-8 if it is not already, to avoid encoding issues
    try:
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    check_imports()
