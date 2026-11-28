---
name: kpl-8bit-video
description: 'Make KPL (Keansburg Premier League) fantasy football videos in the house 8-bit NFL/KPL art style: player stat cards, gameday or holiday promos, recaps, rivalry and season graphics. Use whenever the user asks for a KPL, KPL HQ, House of Heck or other KPL team video, promo, card, recap or showcase, or asks to keep a consistent KPL video style. Built on kpl8bit/ in this repo plus the ffmpeg-skill.'
---

# KPL 8-bit video kit

Everything lives in `kpl8bit/` at the repo root. Read `kpl8bit/README.md` (how to build) and `kpl8bit/STYLE.md` (the art rules) before making anything.

## Workflow

1. **Data first, never by hand.** Use the site feed (`kplhq.kplredzone.workers.dev/api/fantasy`, `/api/nfl`), ESPN (`tools/data/fetch_weeks.sh`, athlete API) and the Flaim connector for 2018–2021 history or live matchup detail. If a host is blocked, ask to add it to the environment. Put "AS OF" stamps on live numbers.
2. **Start from a template.** Copy `templates/<kind>` to `examples/<new-name>` (two levels under `kpl8bit/`, because pages load `../../lib` and `../../assets`), then generate `data.json` with the matching builder in `tools/data/`. Wording overrides go in a `copy.*.json` passed with `--copy`.
3. **Pick a theme** from STYLE.md. **Default to `kpl` (KPL HQ blue).** Use `thanksgiving` for the holiday, and `hoh`/`feast` (House of Heck crimson) only when a video is about House of Heck and asks for that look; `rivalry` is for Rivalry Week. New visual pieces go into `lib/kpl8.js` / `lib/kpl8.css` so the next video reuses them. Don't fork styles per video.
4. **Preview before rendering:** `W=1080 H=1920 node tools/render.js <folder> /tmp/prev 30 <dur> t1,t2,...`. Look at the frames, check text against frame edges, the 14 px minimum and the Reels right-edge zone, then fix.
5. **Build:** `tools/make_video.sh <folder> <duration> reels|youtube`. This renders, adds `sfx.py` effects (no music: house preference) and runs the ffmpeg-skill sequence, audio, export, check and look steps. Report in the ffmpeg-skill format.
6. **Small fixes:** re-render only the affected frames with `FROM=`/`TO=` on `tools/render.js`, then re-run the assemble steps.

## Rules that matter most

- **Data honesty:** verify against a second source when one exists. If a user-supplied graphic disagrees with the data, use the data and say what changed.
- **No NFL team logos:** use abbreviations in team colours. KPL logos come only from `assets/logos` (slot map in `logos.json`). Show current team names only.
- **Player sprites:** `tools/pixelate.py` on the ESPN headshot (`a.espncdn.com/i/headshots/nfl/players/full/<id>.png`), saved as `assets/players/<id>_hero.png`.
- **Render location:** heavy renders go in the scratchpad or `/tmp`. Frames and MP4s are git-ignored.
