#!/bin/bash
# notes/fg04-evidence/locked-rows.sh — one locked run of a tree's pty rows,
# measured, under a stall level.
#
#   locked-rows.sh LEVEL TREE BIN ROWS OUT [measure|plain]
#
# LEVEL 0 runs unloaded (default QoS, no load); LEVEL N >= 1 runs the rows
# and the game inside stall.py's background clamp beside N busy processes.
# `measure` (the default) runs the rows through measure.py (every session
# recorded, the rows unchanged); `plain` runs them through the engine's own
# runner. Takes the Mac build lock once (the lane's wrapper: the mkdir lock,
# the 8 GiB gate inside it, the 60 s turn after release). HOME and TMPDIR are
# the lane's. Prints `ROWS level=L tree=T exit=N`.
set -u
LEVEL=$1 TREE=$2 BIN=$3 ROWS=$4 OUT=$5 MODE=${6:-measure}
EVID=$(cd "$(dirname "$0")" && pwd)
WRAP=/Users/mfwolffe/lanes/fg04/run
mkdir -p "$OUT"
export HOME=/Users/mfwolffe/lanes/fg04/home
if [ "$MODE" = measure ]; then
    cmd=(python3 -I "$EVID/measure.py" run --tree "$TREE" --bin "$BIN" --rows "$ROWS" --out "$OUT")
else
    cmd=(python3 -I .lair/tools/pty --bin "$BIN" --rows "$ROWS")
fi
if [ "$LEVEL" -gt 0 ]; then
    cmd=(taskpolicy -c background python3 -I "$EVID/stall.py" --load "$LEVEL" -- "${cmd[@]}")
fi
FG04_TREE=$TREE "$WRAP" "${cmd[@]}" >"$OUT/rows.log" 2>&1
rc=$?
echo "ROWS level=$LEVEL tree=$TREE exit=$rc $(date +%H:%M:%S)"
exit "$rc"
