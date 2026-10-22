---
name: devlog-video
description: Make the next "Day N of making the best Roblox civilization game" TikTok for Andrea's Fantasy Civilization devlog series, from a gameplay clip to a finished 9:16 MP4 and caption. Use when Andrea sends a new devlog clip or says "make Day N".
---

# Make a Day N devlog TikTok

Andrea is non-technical. Keep messages short and plain. Andrea posts to TikTok themself and adds a trending sound there, so **never add music**.

## 0. Read first (every time)

- `docs/tiktok-roblox/style-guide.md` (house style; section 9 is the pre-export checklist)
- `docs/tiktok-roblox/channel-info.md` (game, narrator, assets)
- `docs/tiktok-roblox/devlog-editor/README.md` (how the scripts work)
- Project memory, for Andrea's latest feedback on earlier days.

The setup hook should already have installed the tools. Check quickly: `ls ~/kokoro ~/fonts && python3 -c "import kokoro_onnx, faster_whisper, cv2"`. If something is missing, run `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh`.

## 1. Get the clip

- Clips usually come as a Google Drive "anyone with the link" share. Download with
  `curl -L -o "$DEVLOG_WORK/src/clip.mp4" "https://drive.usercontent.google.com/download?id=<FILE_ID>&confirm=t"`.
- Chat uploads of videos fail and copying big files from Andrea's computer times out, so ask for a Drive link if there is none.
- Check it: `ffprobe` for size, length, fps. Note the aspect ratio. A thin wide strip needs the card layout; full screen can be cropped bigger.

## 2. Find the moments and write the script

- Use Andrea's timestamps first. Otherwise sample frames (every 1-2 s) and look at them.
- Script: 15-25 s, 4-6 short lines. Line 1 is the hook: "Day N of making the best civilization game on Roblox!" Last line teases the next day and asks to follow.
- Show the plan in one short message (lines + which moments) only if this day adds a new kind of content. Otherwise just make it.

## 3. Build

```bash
export DEVLOG_WORK=/tmp/devlog-work
mkdir -p $DEVLOG_WORK/{src,vo,frames}
cp docs/tiktok-roblox/devlog-editor/day1-example/*.py $DEVLOG_WORK/
```

1. Edit `vo3.py` lines, run it. Read `vo/words.json` for timings.
2. Edit `render.py`: DAY number, `SEGS`, `CAPS` (synced to word timings), `POPS`, `FLASHES`, `SHAKES`, `DUR`, crop. Effects must land on the spoken word.
3. Preview frames first: `python render.py preview 0.5 3.0 7.0 ...`, look at them, fix, then render the full video.
4. Edit `mix.py` (narration placement, SFX events on cuts/pops/hits), run it.
5. Mux and normalize to -14 LUFS (command in the editor README).

## 4. Andrea's rules (keep these)

- Effects strong but not cluttered: orbits, glow, speed ramps, zoom-throughs, punch zooms, flashes on hits.
- Motion graphics (rarity reveal, "Day N/30" bar, arrows on new things, logo fly-in) 1-2 per video. Weapon stat cards rarely, about 1.5 s.
- Emoji / reaction GIFs (project files `reaction-pics/`): at most 1-2 per video. No anime clips or GIFs (copyright).
- Logo: project files `brand/logo-text-transparent.png`.
- Keep text and faces out of TikTok's button areas (right edge and bottom).

## 5. Check before sending

- Run the style guide's pre-export checklist.
- Look at 6-8 frames at phone size (scale to about 360 px wide). Check readable captions, nothing cut off, no more than 2 emojis.
- `ffmpeg -i out.mp4 -af ebur128 -f null -` should show about -14 LUFS. Check that the length matches the plan.

## 6. Deliver

- Save as project files `videos/dayN-fantasy-civilization.mp4` and attach it in the reply.
- Give a caption: one line, one question to get comments, 3-5 hashtags (`#roblox #robloxgames #robloxdev` + game name). Credit Noto emoji (CC BY 4.0) in the description if any were used.
- If Andrea gives feedback, update `style-guide.md` / project memory so the next day already includes it. If you changed the scripts in a way worth reusing, copy them back to `devlog-editor/` in the repo.
