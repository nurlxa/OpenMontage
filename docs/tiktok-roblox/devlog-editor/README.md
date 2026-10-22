# Devlog video editor

Scripts that made the Day 1 "Fantasy Civilization" TikTok (`videos/day1-fantasy-civilization.mp4` in the project files). They are the starting point for every new "Day N" video. The `/devlog-video` skill (`.claude/skills/devlog-video/`) walks through using them.

The tools they need (ffmpeg, Kokoro voice, faster-whisper, OpenCV, Lilita One font) are installed automatically at the start of each cloud session by `.claude/hooks/session-start.sh`.

## Files in `day1-example/`

| File | What it does | What to change per video |
|------|--------------|--------------------------|
| `vo3.py` | Makes the narration lines with Kokoro (voice `am_puck`, speed 1.1) and gets word timings with faster-whisper. Writes `vo/<line>.wav` and `vo/words.json`. | The `secs` dict (the script lines). |
| `render.py` | Draws every frame: top band (DAY N chip + game name), rounded gameplay card with tilt, punch zooms, shake and flashes, word pops, captions under the card. Run `python render.py preview 1.0 4.5 ...` to save single frames to `frames/` instead of rendering. | `SEGS` (which part of the clip plays when), `FLASHES`, `SHAKES`, `CAPS`, `POPS`, `DUR`, the crop (`CW`, `CH`, `BASE_CX`, `BASE_CY`) and the DAY number. |
| `mix.py` | Mixes narration, SFX events and game audio (game audio about 14 dB under the voice). Writes `mix_raw.wav`. | `DUR`, where each narration piece goes, the SFX event list. |

All three use a working folder from the `DEVLOG_WORK` environment variable (default `/tmp/devlog-work`). Put the source clip at `$DEVLOG_WORK/src/clip.mp4`, copy the scripts into `$DEVLOG_WORK`, and make the `vo/` and `frames/` folders.

## Final step (not in the scripts)

Join the picture and sound, and set loudness to -14 LUFS:

```bash
ffmpeg -y -i "$DEVLOG_WORK/video_noaudio.mp4" -i "$DEVLOG_WORK/mix_raw.wav" \
  -af loudnorm=I=-14:TP=-1 -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```

## Notes

- Day 1's source was an ultra-wide Snipping Tool strip (2374x612), so the gameplay sits in a card. A full-screen 16:9 recording can fill more of the frame: change the crop and card size.
- SFX paths point to the project files `sfx/` folder.
