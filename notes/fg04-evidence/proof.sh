#!/bin/bash
# notes/fg04-evidence/proof.sh — fg04's proof under the forced stall.
#
#   proof.sh ROWS OUT TRUNK_TREE HEAD_TREE BIN LEVEL ...
#
# For each LEVEL, head runs 1..20, and before head runs 1, 5, 9, 13 and 17 a
# trunk run, interleaved so both meet the same machine, hour and load. Each run
# is its own locked run (locked-rows.sh: the Mac lock once, the 8 GiB gate, the
# 60 s turn after release) of the named rows through measure.py --light (every
# session's pids recorded; a game a failed trunk row abandoned is ended by its
# recorded pid). Both trees run the same binary (src/ is byte-identical).
# Prints `PROOF <label> level=L run=K exit=N`; any exit but 0 or 1 is no
# verdict and stops it.
set -u
ROWS=$1 OUT=$2 TRUNK=$3 HEAD=$4 BIN=$5; shift 5
HERE=$(cd "$(dirname "$0")" && pwd)
for level in "$@"; do
    for k in $(seq -w 1 20); do
        specs=()
        case $k in 01|05|09|13|17) specs+=("trunk:$TRUNK") ;; esac
        specs+=("head:$HEAD")
        for spec in "${specs[@]}"; do
            label=${spec%%:*} tree=${spec#*:}
            dir=$OUT/$label-L$level-$k
            "$HERE/locked-rows.sh" "$level" "$tree" "$BIN" "$ROWS" "$dir" light >/dev/null
            rc=$?
            echo "PROOF $label level=$level run=$k exit=$rc $(date +%H:%M:%S)"
            if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
                echo "PROOF STOPPED: $label level $level run $k exited $rc (no verdict); see $dir/rows.log"
                exit 2
            fi
        done
    done
done
echo "PROOF DONE"
