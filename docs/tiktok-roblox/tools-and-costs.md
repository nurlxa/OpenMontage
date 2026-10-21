# Tools, Costs, and Limits

Checked on 2026-10-21 in the cloud environment Claude runs in. Always re-check with the registry preflight in `AGENT_GUIDE.md` — availability can change.

## What we use, and whether it's free

| Job | OpenMontage tool / part | Cost | Status in Claude's cloud setup |
|-----|-------------------------|------|-------------------------------|
| Plan and run the edit | `hybrid` pipeline (`clip-factory` for many clips from one long video) | Free | Works |
| Cut, trim, speed up/slow down, join | `video_trimmer`, `video_stitch`, `video_compose` (FFmpeg) | Free | Works |
| Turn wide gameplay into vertical 9:16 | `auto_reframe` (center crop) or blurred-background layout in FFmpeg | Free | Works (center crop; face tracking not needed for gameplay) |
| Animated text pops, titles, end card | HyperFrames (`hyperframes_compose`) | Free | Works |
| Captions from a written script | `subtitle_gen`, `remotion_caption_burn` (FFmpeg fallback) | Free | Works |
| Find exciting moments | `scene_detect`, `audio_energy`, `frame_sampler`, `video_analyzer` | Free | Works |
| Auto-captions of Andrea's **voice** | `transcriber` (Whisper) | Free | **Not ready**: needs `pip install faster-whisper`, and the cloud network currently blocks downloading the speech model. Workaround: Andrea types what was said, or skip voice captions. |
| Remotion (alternative animation engine) | `remotion-composer/` | Free | Not installed yet (`npm install` needed). HyperFrames covers our needs. |
| Sound effects (whoosh, pop, ding, boom) | No built-in SFX pack | Free | **Missing.** See "Sound effects" below. |
| Background music | Added by Andrea in the TikTok app | Free | Recommended path |
| AI voiceover (narrator voice) | `tts_selector` → ElevenLabs, OpenAI, Google, etc. | **Paid API key** | Not configured. Optional. |
| AI images / AI video clips | `image_selector`, `video_selector` (FAL, OpenAI, Kling, etc.) | **Paid API key** | Not configured. Not needed for gameplay videos. |
| AI music | `music_gen` / Suno / ElevenLabs | **Paid API key** | Not configured. Not needed (use TikTok sounds). |

**Bottom line:** the whole style in `style-guide.md` can be done for **$0**. Paid keys only add extras like an AI narrator voice.

## Sound effects

OpenMontage has no sound-effect library, and the free online sound sites (Pixabay, Freesound) are blocked from Claude's cloud environment. Options, best first:

1. **Andrea uploads a free SFX pack once** (10–20 short sounds: whoosh, pop, ding, boom, record scratch, ticking, cartoon fall, crowd "oooh"). Claude keeps them in the project files under `sfx/` and reuses them in every video.
2. Claude generates simple synthetic SFX (whoosh, pop, beep) with FFmpeg. They work but sound basic.

Make sure any pack is free for commercial use. Avoid copyrighted meme sounds ripped from shows.

## Known limits (be honest about these)

- **No direct TikTok posting.** Claude delivers the MP4; Andrea uploads it in the TikTok app.
- **Upload size.** Large screen recordings can fail to upload into the chat. Trim first; keep clips under ~3 minutes.
- **Fresh workspace each session.** Claude's cloud machine starts clean. Anything that must be reused (SFX pack, game logo, fonts, finished videos) must live in the project files or this repo, not just "on Claude's machine".
- **Claude watches video by sampling frames**, not like a person. Andrea's timestamps of the best moments save a lot of time and make edits better.
- **Roblox footage only shows what was recorded.** Claude can't play the game or capture new gameplay.
- **Links:** TikTok may not allow a clickable bio link on new personal accounts, so videos should show the exact game name viewers can search on Roblox.
