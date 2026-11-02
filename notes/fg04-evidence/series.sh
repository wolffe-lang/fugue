#!/bin/bash
# notes/fg04-evidence/series.sh — locked runs, one per (level, tree) pair, in order.
#
#   series.sh ROWS MODE OUTROOT RUNS LEVEL:LABEL:TREE:BIN ...
#
# For run k = 1..RUNS, each spec in turn: one locked-rows.sh run (the Mac lock
# taken once per run, the 60 s turn after each release) into
# OUTROOT/<label>-L<level>-<k>/. Interleaving the specs gives them the same
# machine, hour and load. Prints every run's line; a run that exits other than
# 0 or 1 (3: the memory gate refused; 2: no binary) is no verdict and stops it.
set -u
ROWS=$1 MODE=$2 OUT=$3 RUNS=$4; shift 4
HERE=$(cd "$(dirname "$0")" && pwd)
for k in $(seq -w 1 "$RUNS"); do
    for spec in "$@"; do
        IFS=: read -r level label tree bin <<<"$spec"
        dir=$OUT/$label-L$level-$k
        "$HERE/locked-rows.sh" "$level" "$tree" "$bin" "$ROWS" "$dir" "$MODE"
        rc=$?
        echo "SERIES $label level=$level run=$k exit=$rc $(date +%H:%M:%S)"
        if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
            echo "SERIES STOPPED: $label level $level run $k exited $rc (no verdict); see $dir/rows.log"
            exit 2
        fi
    done
done
echo "SERIES DONE"
