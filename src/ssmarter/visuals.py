import os, math, random, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SPACE_WORDS = ["space", "star", "planet", "venus", "neutron", "galaxy", "orbit", "pulsar"]
HISTORY_WORDS = ["history", "war", "king", "mansa", "empire", "ancient", "military"]
ANIMAL_WORDS = ["animal", "octopus", "tardigrade", "bear", "blood"]
GEO_WORDS = ["geography", "island", "ocean", "earth", "point nemo", "pacific"]
BODY_WORDS = ["body", "stomach", "acid", "human"]
MONEY_WORDS = ["money", "gold", "wealth", "trade", "price"]

def _rng(seed_text):
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16)
    return random.Random(seed)

def gradient(w, h, top, bottom):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        p = y / max(1, h-1)
        arr[y, :, :] = [int(top[i]*(1-p)+bottom[i]*p) for i in range(3)]
    return Image.fromarray(arr)

def starfield(draw, rng, w, h, count=250):
    for _ in range(count):
        x, y = rng.randrange(w), rng.randrange(h)
        r = rng.choice([1,1,1,2,2,3])
        c = rng.randrange(150, 256)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(c,c,min(255,c+30)))

def draw_neutron(draw, rng, w, h, cx=None, cy=None, radius=180):
    cx = cx or int(w*0.65); cy = cy or int(h*0.33)
    for r in range(radius, 0, -8):
        p = r / radius
        col = (int(30+60*p), int(90+120*p), int(180+70*p))
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=col)
    for i in range(9):
        ang = i * math.pi / 9
        x1 = cx + math.cos(ang)*radius*2.2
        y1 = cy + math.sin(ang)*radius*.65
        x2 = cx - math.cos(ang)*radius*2.2
        y2 = cy - math.sin(ang)*radius*.65
        draw.line((x1,y1,x2,y2), fill=(80,150,255), width=4)
    draw.ellipse((cx-38,cy-38,cx+38,cy+38), fill=(255,255,255))

def space_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (4,7,25), (8,24,55))
    draw = ImageDraw.Draw(img, "RGBA")
    starfield(draw, rng, w, h)
    if any(x in text.lower() for x in ["supernova", "dies", "massive"]):
        cx, cy = int(w*.62), int(h*.48)
        for r in range(420, 20, -18):
            col = (255, rng.randrange(80,180), 30, max(10, int(160*r/420)))
            draw.ellipse((cx-r, cy-r//3, cx+r, cy+r//3), outline=col, width=6)
        draw.line((cx,0,cx,h), fill=(80,180,255,190), width=18)
        draw.ellipse((cx-55,cy-55,cx+55,cy+55), fill=(255,255,255,230))
    else:
        draw_neutron(draw, rng, w, h)
    return img.filter(ImageFilter.GaussianBlur(0.2))

def history_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (35,20,12), (90,50,25))
    draw = ImageDraw.Draw(img, "RGBA")
    # parchment/map
    for _ in range(20):
        x, y = rng.randrange(w), rng.randrange(h)
        draw.ellipse((x-220,y-80,x+220,y+80), fill=(180,120,65,25))
    # mountains/city silhouettes
    for i in range(0, w, 180):
        pts = [(i, h*.72), (i+90, h*.55-rng.randrange(80)), (i+180, h*.72)]
        draw.polygon(pts, fill=(25,18,16,190))
    # gold coins/arrows
    for i in range(10):
        x = int(w*.2 + i*w*.07)
        y = int(h*.35 + math.sin(i)*90)
        draw.ellipse((x-32,y-32,x+32,y+32), fill=(255,190,50,210), outline=(255,230,120,255), width=4)
    draw.line((120,h*.30,w-140,h*.50), fill=(255,230,120,170), width=12)
    return img

def animal_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (6,45,50), (10,20,35))
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(9):
        cx, cy = int(w*.6 + math.cos(i)*160), int(h*.45 + math.sin(i*1.5)*220)
        draw.ellipse((cx-100,cy-55,cx+100,cy+55), fill=(180,80,220,130))
        draw.line((cx,cy,cx+rng.randrange(-250,250),cy+rng.randrange(100,420)), fill=(180,100,230,100), width=18)
    draw.ellipse((int(w*.55)-150,int(h*.42)-150,int(w*.55)+150,int(h*.42)+150), fill=(110,70,190,210))
    return img

def geo_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (2,35,80), (2,80,110))
    draw = ImageDraw.Draw(img, "RGBA")
    for r in range(600, 50, -40):
        draw.ellipse((w*.5-r,h*.48-r,w*.5+r,h*.48+r), outline=(80,180,255,30), width=8)
    draw.ellipse((w*.5-90,h*.48-90,w*.5+90,h*.48+90), fill=(20,130,80,230))
    draw.line((w*.15,h*.25,w*.85,h*.70), fill=(255,255,255,160), width=5)
    draw.ellipse((w*.5-18,h*.48-18,w*.5+18,h*.48+18), fill=(255,70,70,255))
    return img

def body_visual(text, w, h):
    img = gradient(w, h, (45,5,20), (10,15,30))
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = int(w*.62), int(h*.48)
    draw.rounded_rectangle((cx-170,cy-260,cx+170,cy+260), radius=170, fill=(230,80,110,170))
    for i in range(7):
        y = cy-200+i*70
        draw.arc((cx-220,y-50,cx+220,y+80), start=0, end=180, fill=(255,160,180,180), width=12)
    return img

def money_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (20,25,12), (60,45,10))
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(22):
        x, y = rng.randrange(80,w-80), rng.randrange(180,h-200)
        r = rng.randrange(28,55)
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(255,190,40,210), outline=(255,240,150,240), width=4)
    draw.line((w*.15,h*.72,w*.85,h*.30), fill=(255,235,100,170), width=16)
    return img

def generic_visual(text, w, h):
    rng = _rng(text)
    img = gradient(w, h, (8,13,22), (18,32,44))
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(14):
        x, y = rng.randrange(w), rng.randrange(h)
        r = rng.randrange(80,220)
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(rng.randrange(50,120),rng.randrange(80,180),rng.randrange(120,255),45))
    return img.filter(ImageFilter.GaussianBlur(1.2))

def make_visual(category, text, w=1080, h=1920):
    key = (category + " " + text).lower()
    if any(k in key for k in SPACE_WORDS): return space_visual(key, w, h)
    if any(k in key for k in HISTORY_WORDS): return history_visual(key, w, h)
    if any(k in key for k in ANIMAL_WORDS): return animal_visual(key, w, h)
    if any(k in key for k in GEO_WORDS): return geo_visual(key, w, h)
    if any(k in key for k in BODY_WORDS): return body_visual(key, w, h)
    if any(k in key for k in MONEY_WORDS): return money_visual(key, w, h)
    return generic_visual(key, w, h)
