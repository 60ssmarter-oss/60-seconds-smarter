import os, random, json, re
from typing import Dict, List

SYSTEM = """You write original, factual YouTube Shorts packages. Keep claims cautious, punchy, advertiser friendly, and easy to visualize. No plagiarism. No dangerous advice. Return only valid JSON."""

HOOKS = [
    "This sounds impossible, but it is real.",
    "This fact feels fake until you understand it.",
    "Here is one of the strangest facts most people never learn.",
    "This tiny detail changes the whole story.",
]

FALLBACK_SCENES = [
    ("HOOK", "{seed}", "slam", "impact"),
    ("THE SETUP", "To understand it, start with the simple version: one extreme condition creates a result that feels almost impossible.", "zoom", "whoosh"),
    ("THE CRAZY PART", "The surprising part is not just that it happened. It is how much one small detail can change the scale of the whole story.", "countup", "boom"),
    ("WHY IT MATTERS", "Facts like this reveal hidden rules behind science, history, nature, and power that we normally never notice.", "pan", "pop"),
    ("REMEMBER THIS", "So the next time someone says trivia is useless, remember: tiny facts can explain enormous things. Follow for another one tomorrow.", "cta", "rise"),
]

def _clean_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:95] if text else "A weird fact you probably missed #shorts"

def make_title(seed: str, category: str) -> str:
    base = seed.split(".")[0].strip()
    templates = [
        f"This {category} fact sounds impossible #shorts",
        f"The weird fact nobody explains #shorts",
        f"This true story is hard to believe #shorts",
        f"{base} #shorts",
    ]
    return _clean_title(random.choice(templates))

def _fallback(topic: Dict) -> Dict:
    seed = topic.get("seed", "A strange fact hides in plain sight.")
    category = topic.get("category", "facts")
    title = make_title(seed, category)
    scenes = []
    for label, line, motion, sfx in FALLBACK_SCENES:
        text = line.format(seed=seed)
        scenes.append({
            "label": label,
            "text": text,
            "visual_prompt": f"cinematic {category} scene about {seed}",
            "motion": motion,
            "sfx": sfx,
        })
    script = " ".join([s["text"] for s in scenes])
    return build_metadata(title, script, category, scenes)

def build_metadata(title: str, script: str, category: str, scenes: List[Dict]) -> Dict:
    hashtags = ["#shorts", "#facts", "#weirdfacts", f"#{category.replace(' ', '')}"]
    description = (
        "A fast, original fact in under 60 seconds.\n\n"
        "Watch to the end and comment which fact shocked you most.\n\n"
        + " ".join(dict.fromkeys(hashtags))
    )
    tags = ["shorts", "facts", "weird facts", category, "education", "60 seconds smarter", "did you know"]
    return {"title": title, "script": script, "description": description, "hashtags": hashtags, "tags": tags, "category": category, "scenes": scenes}

def generate_script(topic: Dict) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback(topic)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = f"""Create one high-retention YouTube Short package.
Category: {topic.get('category')}
Seed fact: {topic.get('seed')}
Angle: {topic.get('angle')}

Return JSON with keys:
- title: <=95 chars, curiosity based, includes #shorts
- script: 105-145 words, conversational narration
- description: 1-2 lines plus hashtags
- hashtags: 4 to 6 hashtag strings
- tags: 8 to 15 SEO tag strings
- scenes: exactly 6 objects, each with label, text, visual_prompt, motion, sfx

Scene rules:
1. Scene 1 must be a 1-2 sentence shock hook.
2. Every scene text should be short enough for captions.
3. Use vivid comparisons but avoid unsupported exact claims.
4. Motions must be one of: slam, zoom, pan, countup, shake, cta.
5. SFX must be one of: impact, whoosh, boom, pop, rise.
"""
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
            temperature=0.85,
            response_format={"type":"json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        scenes = data.get("scenes") or []
        if len(scenes) < 4:
            raise ValueError("AI returned too few scenes")
        category = topic.get("category", "facts")
        title = _clean_title(data.get("title") or make_title(topic.get("seed", ""), category))
        script = data.get("script") or " ".join(s.get("text", "") for s in scenes)
        data = build_metadata(title, script, category, scenes[:6])
        data["description"] = (data["description"] + "\n\n" + (data.get("description") or "")).strip()
        return data
    except Exception as e:
        print(f"AI generation failed, using fallback: {e}")
        return _fallback(topic)
