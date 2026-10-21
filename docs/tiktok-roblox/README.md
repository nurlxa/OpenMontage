# TikTok Roblox Channel — Start Here

This folder is the playbook for making **daily TikTok videos that promote Andrea's own Roblox game**.
It is written for two readers:

- **Andrea** — what to record, what to upload, what to ask for.
- **Claude** (any future session) — how to edit those videos so every one looks the same high-energy style without re-asking.

| File | What it covers |
|------|----------------|
| [style-guide.md](style-guide.md) | The editing "recipe": hook, cuts, zooms, captions, sound effects, loop endings |
| [daily-workflow.md](daily-workflow.md) | Step-by-step daily routine for Andrea and for Claude, plus a copy-paste request template |
| [tools-and-costs.md](tools-and-costs.md) | Which OpenMontage parts we use, what is free, what needs paid keys, and known limits |
| [channel-info.md](channel-info.md) | Facts about the game and the channel (name, link, colors, recurring series). **Fill in once.** |

## What OpenMontage already gives us vs. what this folder adds

OpenMontage (the repo this fork comes from) is a general AI video system. It already ships:

- **Short-form rules** in `skills/creative/short-form.md` — 9:16 size, TikTok safe zones, hook timing, caption sizes, loudness targets.
- **Footage-editing pipelines** — `hybrid` (your recording + added text/graphics) and `clip-factory` (cut many short clips out of one long recording).
- **Free local editing tools** — trimming, joining, vertical reframing, speed changes, captions, animated text (HyperFrames), scene detection.

It does **not** ship anything about Roblox, gaming footage, kid audiences, or promoting a game.
There was no "house style" and no daily routine. That is what this folder adds.

## Ground rules for Claude

1. Read this folder before editing any video for this channel. Use `style-guide.md` as the default creative direction; only ask Andrea about things that are new.
2. Still follow `AGENT_GUIDE.md` (pipelines, preflight, approval gates). The usual pipeline is `hybrid`; use `clip-factory` when Andrea uploads one long session to cut several days of videos from.
3. Default to the **free path** (no paid API calls) unless Andrea has approved a paid tool.
4. Explain things to Andrea in short, simple steps. Andrea is not technical.
