import os, subprocess, shlex

def make_voice(script: str, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    txt = out_path + ".txt"
    wav = out_path
    with open(txt, "w", encoding="utf-8") as f:
        f.write(script)
    # Offline, free, reliable on GitHub Ubuntu after installing espeak-ng.
    cmd = ["espeak-ng", "-v", "en-us", "-s", "165", "-p", "45", "-f", txt, "-w", wav]
    subprocess.run(cmd, check=True)
    return wav
