# Daily Workflow

The fastest way to post every day is **record once, edit several**. One good 15–30 minute play session usually has enough moments for 3–7 TikToks.

## Andrea's part (about 10 minutes a day, or one longer session a week)

### 1. Record

- **On PC:** use a free recorder like OBS Studio or Xbox Game Bar (Windows: press `Win + Alt + R` to start/stop).
- **On phone/tablet:** use the built-in screen recorder.
- Record at **1080p** if possible (60 fps is great, 30 fps is fine).
- Keep your character near the **middle of the screen** — the video gets cropped tall for TikTok, so the edges get cut off.
- Turn off or hide anything private (chat with real names, notifications).
- Talking while you play is optional. If you do, speak clearly — it can become captions.

### 2. Trim before uploading (important)

Big files can fail to upload. Before sending:

- Cut the recording down to the parts with action (phone/PC "Trim" is enough).
- Aim for clips **under ~3 minutes each**. Several short files are better than one huge one.

### 3. Upload and tell Claude what's in it

Upload the clip(s) in the project chat, then send a message like the template below. The more you say about the best moments, the faster and better the edit.

```
New video!
Clip: (attached)
Best moment: around 0:42 — I fall right before the finish 😂
Format: fail / can-you-beat-this / secret / update / noob-vs-pro / other: ___
Hook idea (optional): "ONLY 1% BEAT THIS"
Anything new in the game to mention (optional):
```

If you don't have ideas, just upload and say "make it" — Claude will pick.

### 4. Review and post

- Claude sends back a finished vertical MP4 (and a suggested TikTok caption + hashtags).
- Download it, open TikTok, upload it.
- **Add a trending sound** in TikTok at low volume (Claude leaves room for it).
- Paste the caption/hashtags. Post.

Claude **cannot post to TikTok for you** — that last step is always yours.

## Claude's part

For each request:

1. **Read** `docs/tiktok-roblox/` (this folder) and `channel-info.md`. Read `AGENT_GUIDE.md` rules as usual.
2. **Pick the pipeline:** `hybrid` for one clip → one video; `clip-factory` for one long session → several videos.
3. **Find the moments:** use Andrea's timestamps first. Otherwise use `scene_detect`, `audio_energy` (loud = exciting), and `frame_sampler` to find action.
4. **Plan quickly** (one short message): format, hook text, rough cut list, length. Ask for approval only on the first video of a new format; after that, follow the style guide and just deliver. Don't re-ask things already in this folder.
5. **Edit** per `style-guide.md`: reframe to 9:16, cut dead time, speed ramps, punch-in zooms, text pops, SFX, loop ending, game name.
6. **Check** with the pre-export checklist at the end of `style-guide.md`. Watch sampled frames at phone size.
7. **Deliver**: the MP4 in the project files + a caption suggestion (one line, 1 question to drive comments, 3–5 hashtags like `#roblox #robloxgames #obby` + the game's name).
8. **Remember**: if Andrea gives feedback ("more zooms", "less text"), update `style-guide.md` or `channel-info.md` so the next video already includes it.

## Weekly (optional, 5 minutes)

- Andrea notes which video got the most views/watch time.
- Claude makes more of that format the next week and fewer of the weakest one.
