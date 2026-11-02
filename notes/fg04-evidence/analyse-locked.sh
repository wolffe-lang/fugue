#!/bin/bash
# notes/fg04-evidence/analyse-locked.sh — measure.py's analysis of run
# directories, behind the Mac lock taken once (it runs the game's --apply and
# --headless many times).
#
#   analyse-locked.sh BIN DIR ...
#
# Writes DIR/analysis.log for each DIR and prints `ANALYSE DIR exit=N`.
set -u
BIN=$1; shift
EVID=$(cd "$(dirname "$0")" && pwd)
if [ "${FG04_ANALYSE_INSIDE:-}" = 1 ]; then
    for dir in "$@"; do
        python3 -I "$EVID/measure.py" analyse "$dir" --bin "$BIN" >"$dir/analysis.log" 2>&1
        echo "ANALYSE $dir exit=$? $(date +%H:%M:%S)"
    done
    exit 0
fi
FG04_TREE=$1 FG04_ANALYSE_INSIDE=1 /Users/mfwolffe/lanes/fg04/run "$0" "$BIN" "$@"
