# KPL 8-bit video kit

Everything needed to make KPL HQ videos in one consistent 8-bit NFL/KPL art style: shared styles and pixel art, data builders, a frame renderer, synthesized sound effects, and the finishing pipeline through the repo's ffmpeg-skill.

Read **[STYLE.md](STYLE.md)** before designing anything new.

```
kpl8bit/
  lib/kpl8.css        theme tokens + components (frames, chips, holo card, bug, logos, scanlines)
  lib/kpl8.js         window.K8: easing/timeline, pixel art (leaf, turkey, bat, moon, feast table, wreath),
                      backgrounds (bgKPL, bgHaunted), holo card choreography, charts, slash wipe
  assets/fonts        Press Start 2P, VT323
  assets/logos        KPL HQ site sprite sheets + logos.json (ESPN team slot -> logo letter)
  assets/players      8-bit player sprites (<espnId>.png small, <espnId>_hero.png large)
  templates/          data-driven starting points: copy one per new video
    player-card/      holo stat card: open -> card -> box score -> season chart -> matchup -> outro
  examples/           every video made so far, as reference (index.html + data.json + sfx.py)
  tools/
    render.js         page -> PNG frames (Playwright)
    make_video.sh     frames + sound -> finished, checked MP4
    pixelate.py       ESPN headshot -> 8-bit sprite
    data/             fetch_weeks.sh + builders (player card, Thanksgiving slate, season graphics, rivalries)
```

## How a video works

A video is one HTML page plus a `data.json`. The page exposes two functions:

- `setData(d)` builds the DOM from the data.
- `render(t)` draws the frame at time `t` in seconds.

It has to be a pure function of `t`: no timers, no unseeded randomness. `tools/render.js` steps `t` at 30 fps and screenshots each frame, and `tools/make_video.sh` adds the sound and exports.

## Make a player card (about 10 minutes)

```bash
cd kpl8bit
# 1. data: ESPN weekly files (needs lm-api-reads.fantasy.espn.com allowed in the environment)
tools/data/fetch_weeks.sh /tmp/kplraw 12
# 2. sprite: if assets/players/<id>_hero.png is missing (needs a.espncdn.com allowed)
curl -o /tmp/head.png https://a.espncdn.com/i/headshots/nfl/players/full/<ESPN_ID>.png
mkdir -p /tmp/px && python3 -I tools/pixelate.py /tmp/head.png /tmp/px 76 18 && cp /tmp/px/sprite.png assets/players/<ESPN_ID>_hero.png
# 3. a folder for this video, from the template
cp -r templates/player-card examples/<name>       # must sit two levels under kpl8bit/
python3 -I tools/data/build_player_card.py /tmp/kplraw <ESPN_ID> 12 examples/<name>/data.json            # base KPL blue
#   holiday: --theme thanksgiving --copy templates/player-card/copy.thanksgiving.json
#   House of Heck feast: --theme feast --copy templates/player-card/copy.feast.json
# 4. preview frames, look, then build
W=1080 H=1920 node tools/render.js examples/<name> /tmp/prev 30 31.5 3,8,14,20,26,30
tools/make_video.sh examples/<name> 31.5 reels
```

- **Themes:** `--theme kpl` (default, KPL HQ blue) `|thanksgiving|hoh|feast`. The builder sets `style` and `background`: the blue themes get the starfield and turf, the KPL badge with the leaf wreath and turkey, and the harvest-sun card. `hoh`/`feast` get the haunted castle, the team logo and feast table, and the blood-moon card. `templates/player-card/data.example.json` is the blue Thanksgiving card; `data.feast.json` is the House of Heck feast version (preview it with `DATA=data.feast.json`).
- **Wording:** put wording overrides (titles, kickers, footers) in a small `copy.*.json` and pass it with `--copy`. Numbers always come from ESPN.
- **Breakdown check:** the builder verifies that the scoring breakdown adds up to ESPN's fantasy total and warns if not. Passing, fumbles and 2-point plays aren't modelled yet, so for QBs the breakdown needs extending in `build_player_card.py`.
- **Paths:** pages load `../../lib` and `../../assets`, so a video folder must sit two levels under `kpl8bit/` (for example `examples/<name>`).

## Data sources

| Source | What | Host / tool |
|---|---|---|
| KPL HQ site | Current matchups, rosters, standings, NFL scoreboard | `kplhq.kplredzone.workers.dev/api/fantasy`, `/api/nfl` |
| ESPN fantasy | Weekly player points, projections, stat lines, schedule, draft ranks | `lm-api-reads.fantasy.espn.com` (2022 on) |
| Flaim connector | Seasons ESPN keeps private (2018–2021); live matchup detail | `get_matchups` (MCP) |
| ESPN athlete API | Season stats, game logs | `site.web.api.espn.com` |
| ESPN headshots | Player sprites | `a.espncdn.com` |

## Examples

| Folder | Video | Size / length |
|---|---|---|
| `week11-gameday-promo` | Week 11 gameday promo (first 8-bit piece); its `sfx.py` is the chiptune generator, run with `--sfx-only` | 1080×1920, 20 s |
| `corum-showcase-8bit` | Blake Corum E-Team showcase with a postgame Baja Blast scene | 1080×1920, 31.6 s |
| `thanksgiving-promo` | KPL Thanksgiving Day promo plus the mid-season report | 1080×1920, 68.4 s |
| `rivalry-week` | Rivalry Week 12, head-to-head records since 2018 | 1920×1080, 60.4 s |
| `gibbs-season-card-hoh` | Jahmyr Gibbs season card in House of Heck colours | 1080×1920, 31.6 s |
| `gibbs-thanksgiving-card` | Gibbs Thanksgiving week 12 card: **the base blue KPL look**, reproduced by the template's default `data.example.json` | 1080×1920, 24.6 s |
| `house-of-heck-feast` | "A Thanksgiving Feast at the House of Heck" (House of Heck variant; `templates/player-card` reproduces it with `data.feast.json`) | 1080×1920, 31.5 s |

The examples are standalone pages, written before the shared library existed. New work should start from `templates/`, and anything reusable from an example belongs in `lib/` first.
