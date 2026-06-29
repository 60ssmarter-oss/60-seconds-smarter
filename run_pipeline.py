from src.ssmarter.config import Config
from src.ssmarter.topics import choose_topic
from src.ssmarter.script_generator import generate_script
from src.ssmarter.voice import make_voice
from src.ssmarter.video_builder import build_video
from src.ssmarter.uploader import upload
from src.ssmarter.utils import ensure_dir, save_json, slugify, now_stamp
import os


def main():
    cfg = Config()
    ensure_dir(cfg.output_dir)

    topic = choose_topic()
    package = generate_script(topic)
    stamp = now_stamp()
    slug = slugify(package["title"].replace("#shorts", ""))
    base = os.path.join(cfg.output_dir, f"{stamp}-{slug}")

    metadata_path = base + ".json"
    audio_path = base + ".wav"
    video_path = base + ".mp4"

    save_json(metadata_path, {"topic": topic, "package": package})
    make_voice(package["script"], audio_path)
    build_video(package, audio_path, video_path, cfg)

    print("VIDEO:", video_path)
    print("TITLE:", package["title"])
    print("DESCRIPTION:", package["description"])

    if cfg.upload_to_youtube:
        upload(video_path, package, privacy=cfg.youtube_privacy)
    else:
        print("UPLOAD_TO_YOUTUBE is false; saved video as artifact only.")

if __name__ == "__main__":
    main()
