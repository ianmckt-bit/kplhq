# KPL 8-bit style guide

The rules that make every KPL HQ video look like it came from the same studio. `lib/kpl8.css` and `lib/kpl8.js` implement them. When a rule and your taste disagree, follow the rule, or change the rule here first.

## 1. The look in one line

8-bit KPL HQ arcade: Press Start 2P type, black/edge/black pixel frames with a drop slab, scanlines and a vignette over everything, and pixel art drawn on a grid. Data animates smoothly, but the world it lives in is pixels.

## 2. Formats

| Use | Size | Body class | Export preset |
|---|---|---|---|
| Reels, TikTok, Shorts (default) | 1080×1920 | `v` | `reels` |
| YouTube, X | 1920×1080 | `h` | `youtube` |

- Always 30 fps.
- Keep text 70 px or more from the left and right edges.
- Leave the top 130 px and the bottom 160 px for the corner bug and the turf or skyline.
- Reels and TikTok buttons cover the right edge of the lower half. Don't park key numbers there.

## 3. Themes (colour tokens)

Pick one theme per video with `class="theme-<name>"` on `<body>`. Never hard-code colours that a token already covers.

**`kpl` (KPL HQ blue) is the base theme and the default for everything.** `thanksgiving` is its holiday variant. `hoh` and `feast` are House of Heck team variants: use them only when a video is about House of Heck and asks for that look.

| Theme | Use for | Background | Accent / accent 2 | Frame edge |
|---|---|---|---|---|
| `kpl` | **Base (default)**: gameday, recaps, promos, cards | navy `#020f3d` starfield and turf | yellow `#ffe32b` / orange `#ff8a1f` | white |
| `thanksgiving` | Holiday KPL (Thanksgiving promo, Gibbs card) | navy, falling leaves | yellow / orange | orange |
| `hoh` | House of Heck team pieces | crimson night `#0b0306`, castle, bats | amber `#f2a52b` / orange | bone `#c6b0a3` |
| `feast` | House of Heck × Thanksgiving | crimson night, leaves, moon, castle | amber / orange | orange |
| `rivalry` | Rivalry Week (16:9) | sunset checkerboard `#140904` | gold `#f5b400` / coral `#ff6a3d` | brown |

Team themes follow the team's real logo colours, sampled from the site sprite. A new team theme starts by sampling that team's logo, as in `examples/house-of-heck-feast`.

## 4. Typography

- **Press Start 2P** (`PS2P`) for everything.
- **VT323** (`VT`) only for scoreboard clocks.

| Role | Size | Style |
|---|---|---|
| Title | 48–60 px | `.title` / `.big` (shadow in the shade colour, then black) |
| Kicker above a title | 18–22 px | accent 2 |
| Big number | 64–150 px | accent, red-ink shadow, glows once it settles |
| Body / label | 14–20 px | |

- **Minimum 14 px.** The video plays at about 36% size on phones.
- Uppercase everything.
- Team names are the current names from the site feed. Never show old ESPN team names.

## 5. Frames and components

- **`.pf` / `.pf-accent`:** the KPL HQ box (6 px black, 12 px edge, 18 px black, and a 24 px drop slab). Every panel uses one.
- **`.panel`:** the gradient fill inside frames. **`.stripes`:** the 135° stripe texture for card art and banners.
- **`.c3`:** three-up chips on the holo card. **`.stat`:** box-score tiles. **`.chip` / `.tag`:** small labels.
- **Holo card** (`.card-wrap` with `.card`, `.face`, `.card-art`, `.holo`), with `K8.cardPose` for the flip, exit and outro choreography.
- **Corner bug** `.bug`: league or team logo, "KPL HQ", and the episode line.

## 6. Motion

- **Data and graphics move smoothly** (`K8.spr` spring, `K8.sine` count-ups). Numbers always count up into place, then glow.
- **The pixel world snaps** (`K8.snap`): leaves, stars, embers and bats sit on a 4–6 px grid.
- **Entrances:** `K8.fin` (spring in), `K8.slam` (NFL-style 2.4× → 1× slam for titles and VS), and stagger lists by 0.1–0.2 s.
- **Cuts:** `K8.slashWipe` between scenes, in the theme's colours.
- **Accents:** a white flash plus screen shake only on big moments (title slam, blowouts).
- **Pacing:** fast scenes run 2–4 s; data scenes run 5–6 s and hold the final state for at least 1.5 s.

## 7. Data effects (they must match the data)

| Effect | Trigger |
|---|---|
| Ember particles | Streak of 3+, or a fantasy game of 40+ points |
| Shake, flash and RGB split | Margin of 60+ |
| Flickering "PHOTO FINISH" tag | Margin under 3 |
| "ALL SQUARE" pulse | Tied series |
| Glowing frame | Lead of 3+ |
| Crown | Season high only |

## 8. Pixel art library (`K8.*`)

- `leaf`, `wreath` (leaf ring), `turkey`, `bat`, `moon` (blood moon / harvest sun), `feast` (table with roast turkey, candles, pumpkins and pie).
- Backgrounds: `bgKPL` (starfield and turf), `bgHaunted` (castle skyline with lit windows).
- Player sprites come from ESPN headshots run through `tools/pixelate.py`, at about 56–78 px wide with 16–18 colours and a black outline. They're always drawn with smoothing off.
- Never use NFL team logos. Use team abbreviations in team colours instead. KPL logos come only from the site sprite sheets.

## 9. Sound

- **Effects only, no music bed.** That's the house preference, set on the first promo.
- Square-wave blips and triangle kicks, synthesized in Python per video (`sfx.py`), with every event timed to the page's timeline.
- Count-ups tick, slams get a kick and crash, cards and records get coin sounds. Holiday cues: gobble, candle crackle, organ swell (House of Heck).
- Normalized by the export step to about -14 LUFS with a -1 dBTP true peak.

## 10. Data honesty

- Every number is computed from ESPN, Flaim or the KPL HQ site feed, never typed in by hand.
- Live numbers carry an "AS OF" timestamp on screen.
- Check against a second source when one exists, for example the box score against the fantasy points breakdown, or rivalry records against the old graphics.
- If a supplied graphic disagrees with the data, use the data and tell the user what changed.
