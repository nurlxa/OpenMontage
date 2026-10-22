import os
WORK = os.environ.get("DEVLOG_WORK", "/tmp/devlog-work")  # working folder for this video
import cv2, numpy as np, json, subprocess, math, random, sys, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SRC = WORK + "/src/clip.mp4"
FONT = os.path.expanduser("~/fonts/LilitaOne.ttf")
SFX = "/mnt/project-files/sfx/"
OUT_V = WORK + "/video_noaudio.mp4"
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"

# ---------- layout ----------
TOP = 400                      # top band height
PX, PW = 24, 1032              # panel x / width
CW, CH = 548, 545              # source crop size (hides hotbar)
PH = int(PW * CH / CW)         # 896
PY = TOP
CAP_Y = PY + PH + 22           # caption top
BASE_CX, BASE_CY = 1187, 278

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- timeline ----------
# seg: start, end, src_start, speed, fx dict
SEGS = [
    dict(t0=0.00, t1=1.60, s=53.50, sp=1.0, tilt=(-20, -3), zoom=(1.0, 1.12)),
    dict(t0=1.60, t1=3.30, s=43.80, sp=1.0, punch=1.30, zoom=(1.05, 1.15)),
    dict(t0=3.30, t1=4.85, s=0.00, sp=1.0, zoom=(1.0, 1.10)),
    dict(t0=4.85, t1=6.00, s=2.40, sp=8.2, blur=True, zoom=(1.05, 1.15)),
    dict(t0=6.00, t1=7.60, s=11.95, sp=0.66, punch=1.35, zoom=(1.1, 1.0)),
    dict(t0=7.60, t1=8.90, s=14.50, sp=1.0, zoom=(1.0, 1.1)),
    dict(t0=8.90, t1=9.90, s=17.85, sp=1.0, punch=1.18, tilt=(10, 0)),
    dict(t0=9.90, t1=10.90, s=28.15, sp=1.0, punch=1.18, tilt=(-10, 0)),
    dict(t0=10.90, t1=11.90, s=34.95, sp=1.0, punch=1.18, tilt=(10, 0)),
    dict(t0=11.90, t1=13.30, s=39.10, sp=1.0, punch=1.18, tilt=(-10, 0), zoom=(1.0, 1.08)),
    dict(t0=13.30, t1=14.40, s=68.85, sp=1.0, punch=1.18, tilt=(10, 0)),
    dict(t0=14.40, t1=15.50, s=52.95, sp=0.5, zoom=(1.0, 1.12), dark=(0.0, 0.45)),
    dict(t0=15.50, t1=16.30, s=53.85, sp=0.0, focus=(1350, 430), zoom=(1.15, 1.45), dark=(0.2, 0.0)),
    dict(t0=16.30, t1=17.70, s=53.85, sp=1.0, focus=(1300, 380), zoom=(1.3, 1.0)),
    dict(t0=17.70, t1=18.90, s=78.20, sp=1.0, zoom=(1.0, 1.1), tilt=(-8, 0)),
    dict(t0=18.90, t1=20.40, s=84.50, sp=1.0, zoom=(1.0, 1.12)),
]
DUR = SEGS[-1]["t1"]

FLASHES = [(0.0, 0.25, (255, 255, 255)), (1.60, 0.2, (255, 255, 255)), (6.00, 0.35, (255, 255, 255)),
           (15.55, 0.4, (255, 150, 40)), (17.70, 0.15, (255, 255, 255))]
SHAKES = [(1.62, 0.25, 14), (6.02, 0.4, 26), (12.30, 0.25, 14), (15.57, 0.35, 22)]

# captions (start, end, text, highlight words)
CAPS = [
    (0.15, 1.10, "DAY 1 OF MAKING", {"DAY", "1"}),
    (1.10, 2.25, "THE BEST CIVILIZATION", {"BEST"}),
    (2.25, 3.30, "GAME ON ROBLOX!", {"ROBLOX!"}),
    (3.35, 4.40, "EVERY PLAYER STARTS", set()),
    (4.40, 4.85, "AS A NOOB...", {"NOOB..."}),
    (4.90, 6.00, "BUT ADD SOME ARMOR...", {"ARMOR..."}),
    (6.00, 7.60, "AND BOOM! KNIGHT!", {"KNIGHT!"}),
    (7.65, 8.90, "THEN I MADE 8 WEAPONS", {"8", "WEAPONS"}),
    (14.45, 15.50, "BUT MY FAVORITE...", {"FAVORITE..."}),
    (15.55, 17.70, "THE FURNACE AXE!", {"FURNACE", "AXE!"}),
    (17.80, 18.90, "NEXT UP: MONSTERS", {"MONSTERS"}),
    (18.95, 20.40, "FOLLOW SO YOU DON'T MISS IT!", {"FOLLOW"}),
]
# big pops over the panel: start, end, text, fill, box color
POPS = [
    (4.45, 4.85, "NOOB", (230, 230, 230), (90, 90, 90)),
    (6.30, 7.60, "KNIGHT!", (255, 212, 0), None),
    (8.92, 9.90, "WOODEN SWORD", (255, 255, 255), (150, 95, 40)),
    (9.92, 10.90, "STONE SPEAR", (255, 255, 255), (110, 115, 125)),
    (10.92, 11.90, "STONE CLUB", (255, 255, 255), (110, 115, 125)),
    (11.92, 13.30, "GREATSWORD", (255, 255, 255), (60, 90, 170)),
    (13.32, 14.40, "KATANA", (255, 255, 255), (200, 30, 60)),
    (15.58, 17.70, "FURNACE AXE", (255, 230, 120), (210, 60, 0)),
]
YELLOW = (255, 212, 0)
PINK = (255, 46, 136)

# ---------- text helpers ----------
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

def text_img(words, size, colors, stroke=10, box=None, pad=(36, 18)):
    f = font(size)
    sp = int(size * 0.28)
    widths = [f.getbbox(w, stroke_width=stroke)[2] for w in words]
    tw = sum(widths) + sp * (len(words) - 1)
    th = int(size * 1.25) + stroke * 2
    bw, bh = tw + 2 * pad[0], th + 2 * pad[1]
    im = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box is not None:
        d.rounded_rectangle([10 + 6, 10 + 8, 10 + bw + 6, 10 + bh + 8], radius=28, fill=(0, 0, 0, 140))
        d.rounded_rectangle([10, 10, 10 + bw, 10 + bh], radius=28, fill=box + (255,), outline=(255, 255, 255, 255), width=6)
    x = 10 + pad[0]
    for w, wd, c in zip(words, widths, colors):
        d.text((x, 10 + pad[1] + stroke), w, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += wd + sp
    return np.array(im)

def wrap_words(text, size, maxw, stroke=10):
    f = font(size); words = text.split(); lines = [[]]
    for w in words:
        trial = " ".join(lines[-1] + [w])
        if f.getbbox(trial, stroke_width=stroke)[2] > maxw and lines[-1]: lines.append([w])
        else: lines[-1].append(w)
    if len(lines) > 1 and len(lines[-1]) == 1 and len(lines[-2]) > 2: lines[-1].insert(0, lines[-2].pop()); lines[-1].insert(0, lines[-2].pop())
    return lines

def blit(dst, rgba, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if scale <= 0.01 or alpha <= 0.01: return
    im = rgba
    if abs(scale - 1) > 1e-3:
        im = cv2.resize(im, (max(1, int(im.shape[1] * scale)), max(1, int(im.shape[0] * scale))), interpolation=cv2.INTER_LINEAR)
    if abs(rot) > 0.05:
        h, w = im.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
        im = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    h, w = im.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if xa >= xb or ya >= yb: return
    sub = im[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = sub[..., 3:4] / 255.0 * alpha
    dst[ya:yb, xa:xb] = (dst[ya:yb, xa:xb] * (1 - a) + sub[..., :3] * a).astype(np.uint8)

def pop_anim(t, t0, t1, dur_in=0.22):
    """scale, alpha for a text pop"""
    if t < t0 or t > t1: return 0, 0
    k = (t - t0) / dur_in
    s = 0.6 + 0.4 * back_out(k) if k < 1 else 1.0
    out = clamp((t1 - t) / 0.08)
    return s * (0.9 + 0.1 * out), out

# ---------- source frames ----------
cap = cv2.VideoCapture(SRC)
SRC_FPS = cap.get(cv2.CAP_PROP_FPS) or 30
cache = {}
def src_frame(ts):
    idx = int(round(ts * SRC_FPS))
    if idx in cache: return cache[idx]
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    if not ok:
        idx2 = max(cache) if cache else 0; return cache.get(idx2)
    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    if len(cache) > 400: cache.clear()
    cache[idx] = fr
    return fr

def seg_at(t):
    for s in SEGS:
        if s["t0"] <= t < s["t1"]: return s
    return SEGS[-1]

def src_time(seg, t):
    return seg["s"] + (t - seg["t0"]) * seg["sp"]

def panel_image(seg, t, frame):
    u = (t - seg["t0"]) / (seg["t1"] - seg["t0"])
    z = 1.0
    if "zoom" in seg: z = seg["zoom"][0] + (seg["zoom"][1] - seg["zoom"][0]) * ease_inout(u)
    if "punch" in seg:
        k = ease_out((t - seg["t0"]) / 0.25)
        z *= seg["punch"] + (1.0 - seg["punch"]) * k
    fx, fy = seg.get("focus", (BASE_CX, BASE_CY))
    # move centre toward focus as zoom grows
    m = clamp((z - 1.0) / 0.45)
    cx = BASE_CX + (fx - BASE_CX) * m
    cy = BASE_CY + (fy - BASE_CY) * m
    cw, ch = CW / z, CH / z
    x0 = clamp(cx - cw / 2, 0, frame.shape[1] - cw); y0 = clamp(cy - ch / 2, 0, CH - ch)
    M = np.array([[PW / cw, 0, -x0 * PW / cw], [0, PH / ch, -y0 * PH / ch]], dtype=np.float32)
    return cv2.warpAffine(frame, M, (PW, PH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# rounded mask for panel
mask = np.zeros((PH, PW), np.uint8)
cv2.rectangle(mask, (40, 0), (PW - 40, PH), 255, -1); cv2.rectangle(mask, (0, 40), (PW, PH - 40), 255, -1)
for (x, y) in [(40, 40), (PW - 41, 40), (40, PH - 41), (PW - 41, PH - 41)]: cv2.circle(mask, (x, y), 40, 255, -1)
mask = cv2.GaussianBlur(mask, (3, 3), 0)

def place_panel(canvas, pimg, tilt_deg, ox, oy):
    """draw panel with white border + shadow, with a 3D Y-axis tilt"""
    border = 8
    pw, ph = PW + 2 * border, PH + 2 * border
    card = np.zeros((ph, pw, 4), np.uint8)
    bm = np.zeros((ph, pw), np.uint8)
    cv2.rectangle(bm, (48, 0), (pw - 48, ph), 255, -1); cv2.rectangle(bm, (0, 48), (pw, ph - 48), 255, -1)
    for (x, y) in [(48, 48), (pw - 49, 48), (48, ph - 49), (pw - 49, ph - 49)]: cv2.circle(bm, (x, y), 48, 255, -1)
    card[..., :3] = 255; card[..., 3] = bm
    inner = card[border:border + PH, border:border + PW]
    a = mask[..., None] / 255.0
    inner[..., :3] = (pimg * a + inner[..., :3] * (1 - a)).astype(np.uint8)
    # perspective (rotate around vertical axis)
    th = math.radians(tilt_deg); f = 1800.0
    pts = []
    for (x, y) in [(-pw / 2, -ph / 2), (pw / 2, -ph / 2), (pw / 2, ph / 2), (-pw / 2, ph / 2)]:
        X = x * math.cos(th); Z = x * math.sin(th)
        s = f / (f + Z)
        pts.append((X * s, y * s))
    cx, cy = W / 2 + ox, PY + PH / 2 + oy
    dst = np.float32([(cx + px, cy + py) for px, py in pts])
    src = np.float32([(0, 0), (pw, 0), (pw, ph), (0, ph)])
    Mp = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(card, Mp, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    # shadow
    sh = cv2.GaussianBlur(warped[..., 3], (0, 0), 18).astype(np.float32) / 255.0 * 0.55
    sh = np.roll(np.roll(sh, 14, axis=0), 6, axis=1)
    canvas[:] = (canvas * (1 - sh[..., None])).astype(np.uint8)
    al = warped[..., 3:4].astype(np.float32) / 255.0
    canvas[:] = (canvas * (1 - al) + warped[..., :3] * al).astype(np.uint8)

def background(frame, t):
    c = frame[:, BASE_CX - 172:BASE_CX + 172]
    small = cv2.resize(c, (54, 96), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 2.2)
    bg = cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    bg = bg * 0.5 + np.array([20, 10, 40], np.float32) * 0.5 * 0.6
    return np.clip(bg, 0, 255).astype(np.uint8)

# pre-render static text
CAP_SIZE = 70
cap_imgs = []
for (a, b, txt, hl) in CAPS:
    lines = wrap_words(txt, CAP_SIZE, W - 140)
    ims = [text_img(l, CAP_SIZE, [YELLOW if w in hl else (255, 255, 255) for w in l], stroke=9, pad=(10, 4)) for l in lines]
    cap_imgs.append(ims)
pop_imgs = [text_img([p[2]], 104 if p[2] != "KNIGHT!" else 150, [p[3]], stroke=10, box=p[4]) for p in POPS]
day_chip = text_img(["DAY", "1"], 150, [(255, 255, 255), YELLOW], stroke=12)
game_small = text_img(["FANTASY", "CIVILIZATION"], 64, [(255, 255, 255), (255, 255, 255)], stroke=8, box=PINK, pad=(30, 8))
end_title1 = text_img(["FANTASY"], 130, [YELLOW], stroke=12)
end_title2 = text_img(["CIVILIZATION"], 130, [YELLOW], stroke=12)
end_sub = text_img(["SEARCH", "IT", "ON", "ROBLOX"], 62, [(255, 255, 255)] * 4, stroke=8, box=(0, 170, 255), pad=(28, 6))
legend = text_img(["LEGENDARY"], 60, [(255, 255, 255)], stroke=7, box=(150, 40, 220), pad=(24, 4))
counter_imgs = {n: text_img([str(n)], 230, [YELLOW], stroke=14) for n in range(1, 9)}

def render(t):
    seg = seg_at(t)
    st = src_time(seg, t)
    if seg.get("blur"):
        fs = [src_frame(st + d) for d in (-0.06, -0.03, 0.0)]
        frame = (sum(f.astype(np.float32) for f in fs) / 3).astype(np.uint8)
    else:
        frame = src_frame(st)
    canvas = background(frame, t)
    pimg = panel_image(seg, t, frame)
    u = (t - seg["t0"]) / (seg["t1"] - seg["t0"])
    if "dark" in seg:
        d = seg["dark"][0] + (seg["dark"][1] - seg["dark"][0]) * u
        yy, xx = np.mgrid[0:PH, 0:PW]
        vig = ((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2
        k = 1 - d * np.clip(vig, 0, 1.5)
        pimg = np.clip(pimg * k[..., None], 0, 255).astype(np.uint8)
    tilt = 0.0
    if "tilt" in seg:
        a, b = seg["tilt"]; tilt = a + (b - a) * ease_out(min(1, (t - seg["t0"]) / 0.6 if b == 0 else u))
        if seg is SEGS[0]: tilt += 3 * math.sin(t * 4)
    ox = oy = 0.0
    for (s0, d, amp) in SHAKES:
        if s0 <= t < s0 + d:
            k = 1 - (t - s0) / d
            rnd = random.Random(int(t * 1000))
            ox += rnd.uniform(-amp, amp) * k; oy += rnd.uniform(-amp, amp) * k
    place_panel(canvas, pimg, tilt, ox, oy)

    # top band: DAY 1 chip + game name, end title
    if t < 18.9:
        s, al = pop_anim(t, 0.08, 99)
        blit(canvas, day_chip, W / 2, 160, s, al, rot=-3)
        s2, al2 = pop_anim(t, 0.35, 99)
        blit(canvas, game_small, W / 2, 320, s2, al2)
    else:
        s, al = pop_anim(t, 18.9, 99)
        blit(canvas, end_title1, W / 2, 140, s, al, rot=-2)
        s, al = pop_anim(t, 19.0, 99)
        blit(canvas, end_title2, W / 2, 262, s, al, rot=-2)
        s, al = pop_anim(t, 19.15, 99)
        blit(canvas, end_sub, W / 2, 362, s, al)

    # counter 1..8
    if 7.95 <= t < 8.9:
        n = min(8, 1 + int((t - 7.95) / 0.07))
        sc = 1.0 + 0.25 * (1 - clamp((t - 7.95 - (n - 1) * 0.07) / 0.07)) if n < 8 else (pop_anim(t, 7.95 + 7 * 0.07, 8.9)[0])
        blit(canvas, counter_imgs[n], W / 2, PY + PH / 2 - 40, sc, 1.0, rot=-4)
    # big pops
    for (p, im) in zip(POPS, pop_imgs):
        s, al = pop_anim(t, p[0], p[1])
        if al > 0:
            y = PY + PH - 150 if p[2] not in ("KNIGHT!", "NOOB") else PY + PH / 2 + 120
            rot = -4 if p[2] in ("KNIGHT!", "FURNACE AXE") else 0
            if p[2] == "FURNACE AXE":
                wob = 1 + 0.03 * math.sin(t * 18)
                blit(canvas, im, W / 2, y, s * wob, al, rot)
                s3, al3 = pop_anim(t, 15.95, p[1])
                blit(canvas, legend, W / 2 + 230, y - 105, s3, al3, rot=8)
            else:
                blit(canvas, im, W / 2, y, s, al, rot)
    # captions
    for (c, ims) in zip(CAPS, cap_imgs):
        s, al = pop_anim(t, c[0], c[1], 0.15)
        if al > 0:
            y = CAP_Y + 50
            for im in ims:
                blit(canvas, im, W / 2, y, s, al); y += im.shape[0] - 20
    # flashes
    for (f0, d, col) in FLASHES:
        if f0 <= t < f0 + d:
            a = (1 - (t - f0) / d) ** 2 * 0.85
            canvas[:] = (canvas * (1 - a) + np.array(col) * a).astype(np.uint8)
    return canvas

if __name__ == "__main__":
    if PREVIEW:
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            cv2.imwrite(f"{WORK}/frames/p_{t:05.2f}.jpg", cv2.cvtColor(render(t), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
        sys.exit()
    n = int(round(DUR * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", OUT_V], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(render(i / FPS).tobytes())
        if i % 60 == 0: print(i, n, flush=True)
    p.stdin.close(); p.wait()
    print("done")
