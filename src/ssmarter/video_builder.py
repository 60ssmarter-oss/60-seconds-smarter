import os, math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip as MovieAudio
from .utils import wrap_words
from .visuals import make_visual
from .audio import make_sfx_pack

WHITE = (255,255,255)
YELLOW = (255,214,64)
PINK = (255,145,160)
BLACK = (0,0,0)

def font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def text_size(draw, text, fnt):
    b = draw.textbbox((0,0), text, font=fnt)
    return b[2]-b[0], b[3]-b[1]

def draw_text_stroke(draw, pos, text, fnt, fill=WHITE, stroke=BLACK, sw=4):
    draw.text(pos, text, font=fnt, fill=fill, stroke_width=sw, stroke_fill=stroke)

def fit_lines(text, fnt, max_width, max_lines=5):
    dummy = Image.new("RGB", (10,10)); draw = ImageDraw.Draw(dummy)
    words = text.split(); lines=[]; cur=""
    for word in words:
        test = (cur + " " + word).strip()
        w,_ = text_size(draw, test, fnt)
        if w <= max_width or not cur:
            cur = test
        else:
            lines.append(cur); cur = word
            if len(lines) >= max_lines:
                break
    if cur and len(lines) < max_lines: lines.append(cur)
    return lines

def safe_label(label):
    return re.sub(r"[^A-Z0-9 ?!']", "", label.upper())[:28]

def create_overlay(scene, idx, total, duration, w, h, progress_start, progress_end, channel):
    overlay = Image.new("RGBA", (w,h), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    # dark gradient for readability
    shade = Image.new("RGBA", (w,h), (0,0,0,0))
    sd = ImageDraw.Draw(shade)
    for y in range(h):
        alpha = int(180 * (1 - abs((y/h)-0.42)))
        alpha = max(0, min(145, alpha))
        sd.line((0,y,w,y), fill=(0,0,0,alpha))
    overlay.alpha_composite(shade)

    # top brand pill
    draw.rounded_rectangle((48, 55, 520, 132), radius=32, fill=(6,8,14,220), outline=YELLOW+(255,), width=3)
    draw.ellipse((70,72,112,114), fill=YELLOW+(255,))
    draw.text((130, 75), channel.upper(), font=font(34, True), fill=WHITE+(255,))

    # time badge
    t0 = int(progress_start * 60); t1 = int(progress_end * 60)
    badge = f"0:{t0:02d}-0:{min(59,t1):02d}"
    tw, th = text_size(draw, badge, font(30, True))
    draw.rounded_rectangle((w-tw-96, h-190, w-50, h-130), radius=16, fill=(0,0,0,200))
    draw.text((w-tw-73, h-178), badge, font=font(30, True), fill=WHITE+(255,))

    label = safe_label(scene.get("label", "DID YOU KNOW?"))
    draw_text_stroke(draw, (70, 215), label, font(58, True), fill=YELLOW if idx else PINK, sw=3)

    text = scene.get("text", "")
    # Split into title-like first sentence and supporting caption
    parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    headline = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    if idx == 0:
        head_font = font(92, True); body_font = font(50, False); max_lines=5
    else:
        head_font = font(70, True); body_font = font(46, False); max_lines=4

    y = 320
    for line in fit_lines(headline, head_font, w-140, max_lines):
        # highlight big numbers/keywords in yellow
        color = YELLOW if any(ch.isdigit() for ch in line) or line.upper() in ["DENSE", "IMPOSSIBLE"] else WHITE
        draw_text_stroke(draw, (70,y), line, head_font, fill=color, sw=5)
        y += int(head_font.size * 1.08)

    y += 35
    for line in fit_lines(body, body_font, w-140, 6):
        draw_text_stroke(draw, (70,y), line, body_font, fill=(238,238,238), sw=3)
        y += int(body_font.size * 1.22)

    # icons/number side panel for mid scenes
    if idx in (2,3):
        panel_y = h - 520
        draw.rounded_rectangle((70, panel_y, 500, panel_y+235), radius=28, fill=(0,0,0,160), outline=YELLOW+(190,), width=3)
        big = "!" if idx == 3 else "∞"
        draw.text((105, panel_y+28), big, font=font(120, True), fill=YELLOW+(255,))
        draw.text((205, panel_y+55), "THIS IS\nTHE PART\nPEOPLE MISS", font=font(40, True), fill=WHITE+(255,))

    # bottom progress bar
    bar_x, bar_y, bar_w = 70, h-90, w-140
    draw.rounded_rectangle((bar_x,bar_y,bar_x+bar_w,bar_y+18), radius=9, fill=(255,255,255,70))
    draw.rounded_rectangle((bar_x,bar_y,bar_x+int(bar_w*progress_end),bar_y+18), radius=9, fill=YELLOW+(255,))

    if idx == total-1:
        draw.rounded_rectangle((70, h-350, w-70, h-235), radius=24, fill=(0,0,0,170), outline=YELLOW+(255,), width=3)
        draw.text((105, h-325), "FOLLOW FOR MORE FACTS", font=font(42, True), fill=YELLOW+(255,))
        draw.text((105, h-275), "COMMENT WHAT TOPIC IS NEXT", font=font(36, True), fill=WHITE+(255,))
    return np.array(overlay)

def make_scene_clip(scene, idx, total, scene_duration, package, config, progress_start, progress_end):
    w, h = config.width, config.height
    bg = make_visual(package.get("category", "facts"), scene.get("visual_prompt", scene.get("text", "")), w, h)
    # Build a Ken Burns style background: oversize then crop via resize over time.
    base_arr = np.array(bg)
    motion = scene.get("motion", "zoom")
    def frame(t):
        p = t / max(0.001, scene_duration)
        scale = 1.08 + 0.08*p
        if motion == "shake":
            dx = int(math.sin(p*42)*12); dy = int(math.cos(p*37)*10)
        elif motion == "pan":
            dx = int((p-.5)*90); dy = int(math.sin(p*math.pi)*-35)
        else:
            dx = int(math.sin(p*math.pi*2)*18); dy = int((p-.5)*-50)
        img = Image.fromarray(base_arr).resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        left = (img.width - w)//2 + dx; top = (img.height - h)//2 + dy
        left = max(0, min(img.width-w, left)); top = max(0, min(img.height-h, top))
        crop = img.crop((left, top, left+w, top+h)).convert("RGBA")
        # pulse dark overlay
        draw = ImageDraw.Draw(crop, "RGBA")
        draw.rectangle((0,0,w,h), fill=(0,0,0,55))
        return np.array(crop.convert("RGB"))
    bg_clip = ImageClip(base_arr).set_duration(scene_duration)
    # MoviePy ImageClip cannot animate resize/crop with function cheaply; use VideoClip
    from moviepy.editor import VideoClip
    bg_clip = VideoClip(frame, duration=scene_duration)
    overlay = create_overlay(scene, idx, total, scene_duration, w, h, progress_start, progress_end, config.channel_name)
    overlay_clip = ImageClip(overlay).set_duration(scene_duration)
    # punch-in for first scene overlay
    if scene.get("motion") == "slam":
        overlay_clip = overlay_clip.resize(lambda t: 1.04 - 0.04*min(1,t/.35)).set_position("center")
    return CompositeVideoClip([bg_clip, overlay_clip], size=(w,h)).set_duration(scene_duration)

def build_video(package, audio_path, out_path, config):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    audio = AudioFileClip(audio_path)
    duration = min(audio.duration + 1.2, 59.0)
    scenes = package.get("scenes") or []
    if not scenes:
        scenes = [{"label":"DID YOU KNOW?", "text":package.get("script", ""), "motion":"zoom", "sfx":"impact", "visual_prompt":package.get("title", "")}]
    total = len(scenes)
    # weight first and final slightly shorter for faster pacing
    raw = [0.14] + [0.17]*(total-2) + [0.18] if total > 2 else [1/total]*total
    s = sum(raw); durations = [max(3.2, duration*x/s) for x in raw]
    scale = duration / sum(durations); durations = [d*scale for d in durations]

    clips = []
    elapsed = 0
    for idx, (scene, sd) in enumerate(zip(scenes, durations)):
        ps = elapsed / duration; pe = min(1, (elapsed+sd)/duration)
        clips.append(make_scene_clip(scene, idx, total, sd, package, config, ps, pe))
        elapsed += sd
    video = concatenate_videoclips(clips, method="compose").set_duration(duration)

    sfx_dir = os.path.join(os.path.dirname(out_path), "sfx")
    sfx = make_sfx_pack(sfx_dir)
    audio_tracks = [audio.subclip(0, min(audio.duration, duration)).volumex(1.0)]
    music = MovieAudio(sfx["music"]).subclip(0, duration).volumex(0.45)
    audio_tracks.append(music)
    elapsed = 0
    for scene, sd in zip(scenes, durations):
        name = scene.get("sfx", "whoosh")
        path = sfx.get(name, sfx.get("whoosh"))
        if path:
            audio_tracks.append(MovieAudio(path).set_start(elapsed).volumex(0.75))
        elapsed += sd
    video = video.set_audio(CompositeAudioClip(audio_tracks))
    video.write_videofile(out_path, fps=config.fps, codec="libx264", audio_codec="aac", preset="medium", threads=2, verbose=False, logger=None)
    return out_path
