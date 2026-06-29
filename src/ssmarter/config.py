from dataclasses import dataclass
import os

@dataclass
class Config:
    channel_name: str = os.getenv("CHANNEL_NAME", "60 Seconds Smarter")
    width: int = int(os.getenv("VIDEO_WIDTH", "1080"))
    height: int = int(os.getenv("VIDEO_HEIGHT", "1920"))
    fps: int = int(os.getenv("VIDEO_FPS", "30"))
    duration_seconds: int = int(os.getenv("DURATION_SECONDS", "50"))
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    upload_to_youtube: bool = os.getenv("UPLOAD_TO_YOUTUBE", "false").lower() == "true"
    youtube_privacy: str = os.getenv("YOUTUBE_PRIVACY", "private")
