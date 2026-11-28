#!/usr/bin/env bash
# Fetch ESPN weekly league files (rosters, player stats, fantasy points) for weeks 1..N.
# usage: tools/data/fetch_weeks.sh OUTDIR LAST_WEEK [SEASON] [LEAGUE_ID]
# Needs lm-api-reads.fantasy.espn.com in the environment's allowed hosts. Seasons 2018-2021 are
# private on ESPN; use the Flaim connector (get_matchups) for those instead.
set -euo pipefail
OUT=${1:?outdir}; LAST=${2:?last week}; SEASON=${3:-2026}; LEAGUE=${4:-404068}
mkdir -p "$OUT"
for w in $(seq 1 "$LAST"); do
  curl -sS -m 60 "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/$SEASON/segments/0/leagues/$LEAGUE?view=mMatchup&view=mMatchupScore&view=mTeam&scoringPeriodId=$w" -o "$OUT/wk$w.json" -w "wk$w %{http_code} %{size_download}\n"
done
