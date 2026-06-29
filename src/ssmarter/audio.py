import os, math, wave, random
from pathlib import Path

SAMPLE_RATE = 44100

def _write_wav(path, samples):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            wav.writeframesraw(int(s * 32767).to_bytes(2, "little", signed=True))

def tone(path, duration=0.25, freq=440, volume=0.35, decay=True):
    n = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (1 - i / n) if decay else 1
        samples.append(math.sin(2 * math.pi * freq * t) * volume * env)
    _write_wav(path, samples)
    return path

def noise_hit(path, duration=0.18, volume=0.28):
    n = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(n):
        env = (1 - i / n) ** 2
        samples.append(random.uniform(-1, 1) * volume * env)
    _write_wav(path, samples)
    return path

def riser(path, duration=0.8, start=220, end=880, volume=0.15):
    n = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(n):
        p = i / max(1, n-1)
        freq = start + (end - start) * p
        env = min(1, p * 3) * (1 - max(0, p - .85) * 5)
        t = i / SAMPLE_RATE
        samples.append(math.sin(2 * math.pi * freq * t) * volume * env)
    _write_wav(path, samples)
    return path

def music_bed(path, duration=60, volume=0.045):
    n = int(duration * SAMPLE_RATE)
    notes = [55, 65.4, 73.4, 82.4]
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        bar = int(t // 4) % len(notes)
        base = notes[bar]
        val = 0
        val += math.sin(2 * math.pi * base * t) * 0.65
        val += math.sin(2 * math.pi * base * 2 * t) * 0.25
        val += math.sin(2 * math.pi * base * 3 * t) * 0.10
        pulse = 0.75 + 0.25 * math.sin(2 * math.pi * 0.5 * t)
        samples.append(val * volume * pulse)
    _write_wav(path, samples)
    return path

def make_sfx_pack(folder):
    os.makedirs(folder, exist_ok=True)
    paths = {
        "impact": noise_hit(os.path.join(folder, "impact.wav"), 0.22, 0.35),
        "boom": tone(os.path.join(folder, "boom.wav"), 0.38, 90, 0.42),
        "whoosh": riser(os.path.join(folder, "whoosh.wav"), 0.45, 300, 900, 0.10),
        "pop": tone(os.path.join(folder, "pop.wav"), 0.16, 750, 0.25),
        "rise": riser(os.path.join(folder, "rise.wav"), 0.95, 220, 1200, 0.13),
    }
    paths["music"] = music_bed(os.path.join(folder, "music.wav"), 70)
    return paths
