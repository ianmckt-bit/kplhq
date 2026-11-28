#!/usr/bin/env bash
# Build a finished video from a kit folder (templates/* or examples/*).
# usage: tools/make_video.sh FOLDER DURATION_S [PRESET] [OUTNAME]
#   PRESET: reels (1080x1920, default) | youtube (1920x1080) | any export.py preset
#   Work files go to $WORK (default /tmp/kpl8bit-work/<folder>); the MP4 lands in $WORK/out/.
# Steps: render frames -> sound effects (FOLDER/sfx.py) -> ffmpeg-skill: sequence, audio, export, check, look.
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"; SK="$KIT/../.claude/skills/ffmpeg-skill/scripts"
DIR="$(cd "${1:?folder}" && pwd)"; DUR="${2:?duration seconds}"; PRESET="${3:-reels}"; NAME="${4:-$(basename "$DIR")}"
WORK="${WORK:-/tmp/kpl8bit-work/$(basename "$DIR")}"; FPS="${FPS:-30}"
if [ "$PRESET" = youtube ] || [ "$PRESET" = x ]; then W=1920; H=1080; else W=1080; H=1920; fi
W="${W_OVERRIDE:-$W}"; H="${H_OVERRIDE:-$H}"
mkdir -p "$WORK/out"; rm -rf "$WORK/frames"; export PYTHONDONTWRITEBYTECODE=1
echo "== render $NAME ($W x $H, ${DUR}s @ ${FPS}fps)"
W=$W H=$H node "$KIT/tools/render.js" "$DIR" "$WORK/frames" "$FPS" "$DUR"
echo "== sound effects"
DATA="$DIR/data.json"; [ -f "$DATA" ] || DATA="$DIR/data.example.json"
python3 -I "$DIR/sfx.py" "$DATA" "$WORK/out/sfx.wav"
cd "$WORK/out"
python3 "$SK/sequence.py" --dir "$WORK/frames" --pattern "frame_%04d.png" --fps "$FPS" -o silent.mp4 --overwrite --json-brief >/dev/null
python3 "$SK/audio.py" silent.mp4 --replace sfx.wav -o with_sfx.mp4 --overwrite --json-brief >/dev/null
python3 "$SK/export.py" with_sfx.mp4 --preset "$PRESET" -o "$NAME.mp4" --overwrite --json-brief | grep -E '"status"|duration_s|"size"' || true
python3 "$SK/check.py" "$NAME.mp4" --platform "$PRESET" | grep -E 'FAIL|WARN|checks' || true
python3 "$SK/look.py" "$NAME.mp4" --tiles 3x2 -o "$NAME.sheet.png" | tail -1
echo "== done: $WORK/out/$NAME.mp4"
