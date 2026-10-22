import os
WORK = os.environ.get("DEVLOG_WORK", "/tmp/devlog-work")  # working folder for this video
import numpy as np, soundfile as sf, subprocess, sys
sys.path.insert(0, WORK)
SR = 48000
DUR = 20.4
K = "/mnt/project-files/sfx/kenney/"
B = "/mnt/project-files/sfx/basic/"

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

mix_vo = np.zeros(int(SR * (DUR + 1)), np.float32)
mix_sfx = np.zeros_like(mix_vo)
mix_game = np.zeros_like(mix_vo)

def add(buf, x, t, gain_db=0.0):
    i = int(t * SR); x = x * (10 ** (gain_db / 20))
    n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n]

def fade(x, ms=12):
    n = int(SR * ms / 1000); x = x.copy()
    if len(x) > 2 * n:
        x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x

# ---- narration
vo = {k: load(f"{WORK}/vo/{k}.wav") for k in "ABCDE"}
for k in vo: vo[k] /= np.abs(vo[k]).max() + 1e-9
def piece(k, a, b=None):
    x = vo[k]; return fade(x[int(a * SR): (int(b * SR) if b else len(x))])
add(mix_vo, vo["A"], 0.15)
add(mix_vo, vo["B"], 3.35)
add(mix_vo, piece("C", 0, 1.15), 7.65)
add(mix_vo, piece("C", 1.15, 1.95), 8.95)
add(mix_vo, piece("C", 1.95, 2.75), 9.95)
add(mix_vo, piece("C", 2.75, 3.42), 10.95)
add(mix_vo, piece("C", 3.42, 4.48), 11.95)
add(mix_vo, piece("C", 4.48), 13.35)
add(mix_vo, piece("D", 0, 0.88), 14.45)
add(mix_vo, piece("D", 0.86), 15.48)
add(mix_vo, vo["E"], 17.80)

# ---- sfx
S = {
 "whoosh": load(B + "whoosh.wav"), "boom": load(B + "boom.wav"), "pop": load(B + "pop.wav"),
 "ding": load(B + "ding.wav"), "riser": load(B + "riser.wav"),
 "metal0": load(K + "kenney_impact-sounds/impactMetal_heavy_000.ogg"),
 "metal2": load(K + "kenney_impact-sounds/impactMetal_heavy_002.ogg"),
 "punch": load(K + "kenney_impact-sounds/impactPunch_heavy_001.ogg"),
 "error": load(K + "kenney_interface-sounds/error_004.ogg"),
 "tick": load(K + "kenney_interface-sounds/tick_001.ogg"),
 "confirm": load(K + "kenney_interface-sounds/confirmation_002.ogg"),
 "max": load(K + "kenney_interface-sounds/maximize_006.ogg"),
 "knife1": load(K + "kenney_rpg-audio/drawKnife1.ogg"),
 "knife2": load(K + "kenney_rpg-audio/drawKnife2.ogg"),
 "knife3": load(K + "kenney_rpg-audio/drawKnife3.ogg"),
 "cloth1": load(K + "kenney_rpg-audio/cloth1.ogg"), "cloth2": load(K + "kenney_rpg-audio/cloth2.ogg"),
 "belt": load(K + "kenney_rpg-audio/clothBelt.ogg"),
 "power": load(K + "kenney_digital-audio/powerUp3.ogg"),
}
for k in S: S[k] /= np.abs(S[k]).max() + 1e-9
ev = [
 (0.00, "boom", -6), (0.00, "whoosh", -8),
 (1.60, "whoosh", -10), (1.78, "metal0", -8),
 (3.30, "whoosh", -12), (4.45, "error", -9), (4.45, "pop", -12),
 (4.85, "whoosh", -10), (4.95, "cloth1", -8), (5.30, "belt", -8), (5.65, "cloth2", -8),
 (6.00, "boom", -3), (6.00, "metal2", -6), (6.30, "pop", -10),
 (7.60, "whoosh", -12), (8.44, "confirm", -10),
 (8.90, "whoosh", -12), (8.93, "knife1", -8), (8.95, "pop", -14),
 (9.90, "whoosh", -12), (9.93, "knife2", -8), (9.95, "pop", -14),
 (10.90, "whoosh", -12), (10.93, "knife3", -8), (10.95, "pop", -14),
 (11.90, "whoosh", -12), (11.93, "knife1", -8), (11.95, "pop", -14), (12.30, "punch", -8),
 (13.30, "whoosh", -12), (13.33, "knife2", -8), (13.35, "pop", -14),
 (14.40, "riser", -10),
 (15.52, "boom", -3), (15.52, "metal0", -6), (15.60, "power", -10), (15.95, "max", -10),
 (17.70, "whoosh", -12),
 (18.90, "whoosh", -12), (18.92, "pop", -12), (19.15, "ding", -12),
]
for i in range(8):
    ev.append((7.95 + i * 0.07, "tick", -14))
for t, k, g in ev: add(mix_sfx, S[k], t, g)

# ---- game audio
import importlib.util
spec = importlib.util.spec_from_file_location("r", WORK + "/render.py")
src_all = load(WORK + "/src/clip.mp4")
# segment list copied from render (avoid importing heavy module)
SEGS = [(0.00,1.60,53.50,1.0),(1.60,3.30,43.80,1.0),(3.30,4.85,0.00,1.0),(4.85,6.00,2.40,8.2),(6.00,7.60,11.95,0.66),
 (7.60,8.90,14.50,1.0),(8.90,9.90,17.85,1.0),(9.90,10.90,28.15,1.0),(10.90,11.90,34.95,1.0),(11.90,13.30,39.10,1.0),
 (13.30,14.40,68.85,1.0),(14.40,15.50,52.95,0.5),(15.50,16.30,53.85,0.0),(16.30,17.70,53.85,1.0),(17.70,18.90,78.20,1.0),(18.90,20.40,84.50,1.0)]
for t0, t1, s, sp in SEGS:
    if sp <= 0 or sp > 2: continue
    n_out = int((t1 - t0) * SR)
    a = int(s * SR); b = int((s + (t1 - t0) * sp) * SR)
    seg = src_all[a:b]
    if sp != 1.0:
        seg = np.interp(np.linspace(0, len(seg) - 1, n_out), np.arange(len(seg)), seg).astype(np.float32)
    add(mix_game, fade(seg[:n_out], 8), t0, 0)

def rms_db(x):
    x = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else -99
print("vo", rms_db(mix_vo), "sfx", rms_db(mix_sfx), "game", rms_db(mix_game))
# game audio sits ~14 dB under narration
mix_game *= 10 ** ((rms_db(mix_vo) - 14 - rms_db(mix_game)) / 20)
# duck sfx a little while narration speaks? keep simple
out = mix_vo + mix_sfx * 0.9 + mix_game
out = out[:int(SR * DUR)]
out /= np.abs(out).max() / 0.9
sf.write(WORK + "/mix_raw.wav", out, SR)
print("ok")
