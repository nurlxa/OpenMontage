import os
WORK = os.environ.get("DEVLOG_WORK", "/tmp/devlog-work")  # working folder for this video
import soundfile as sf, numpy as np, json
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel
from scipy.signal import resample_poly
k = Kokoro(os.path.expanduser("~/kokoro/kokoro-v1.0.onnx"), os.path.expanduser("~/kokoro/voices-v1.0.bin"))
secs = {"A":"Day one of making the best civilization game on Roblox!",
"B":"Every player starts as a noob. But add some armor... and BOOM! Knight!",
"C":"Then I made eight weapons. Wooden sword! Stone spear! Stone club! A giant greatsword! And a katana!",
"D":"But my favorite... the Furnace Axe!",
"E":"Next up: monsters. Follow so you don't miss it!"}
m=WhisperModel('small.en',device='cpu',compute_type='int8')
out={}
for n,t in secs.items():
    s, sr = k.create(t, voice="am_puck", speed=1.1, lang="en-us")
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-240):idx[-1]+2400]
    sf.write(f"{WORK}/vo/{n}.wav", s, sr)
    x=resample_poly(s,2,3).astype(np.float32)
    segs,_=m.transcribe(x,word_timestamps=True, initial_prompt=t)
    ws=[(w.word.strip(),round(float(w.start),2),round(float(w.end),2)) for sg in segs for w in sg.words]
    out[n]={"dur":round(len(s)/sr,2),"words":ws}; print(n,out[n]["dur"],ws)
json.dump(out,open(f"{WORK}/vo/words.json","w"))
