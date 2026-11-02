#!/bin/bash
# notes/fg04-evidence/gauntlet.sh — the final-head gauntlet on the Mac.
#
#   FG04_TREE=<pinned tree> ~/lanes/fg04/run notes/fg04-evidence/gauntlet.sh
#
# Every line of tools/check (the macOS gate), in its order, each run bare with
# its exit read directly, the injector's own rows first. Stops at the first nonzero
# step; prints `BEGIN <step>` and `END <step> exit=N` for every step it runs.
set -u
cd "$(dirname "$0")/../.."
export HOME=/Users/mfwolffe/lanes/fg04/home
step() {
    name=$1; shift
    echo "BEGIN $name $(date +%H:%M:%S)"
    "$@"
    rc=$?
    echo "END $name exit=$rc $(date +%H:%M:%S)"
    if [ "$rc" -ne 0 ]; then echo "GAUNTLET STOPPED at $name"; exit "$rc"; fi
}
step paced-unit python3 -I tests/test_paced.py
step storm-unit python3 -I tests/test_storm_frames.py
step lair-check .lair/tools/check
step goldens-native .lair/tools/goldens --bin target/native/fugue
step gameplay-native python3 -I tools/gameplay.py --bin target/native/fugue
step gameplay-release python3 -I tools/gameplay.py --bin target/release/fugue
step glyphs python3 -I tools/glyphs.py
step staff-native python3 -I tools/staff-check.py --bin target/native/fugue
step staff-release python3 -I tools/staff-check.py --bin target/release/fugue
step species-native python3 -I tools/species-gameplay.py --bin target/native/fugue
step species-release python3 -I tools/species-gameplay.py --bin target/release/fugue
step pitch-native python3 -I tools/pitch-check.py --bin target/native/fugue
step pitch-release python3 -I tools/pitch-check.py --bin target/release/fugue
step fugue-native python3 -I tools/fugue-gameplay.py --bin target/native/fugue
step fugue-release python3 -I tools/fugue-gameplay.py --bin target/release/fugue
step pty-native python3 -I .lair/tools/pty --bin target/native/fugue --rows own-cantus-session,own-cantus-fux-keys,enhanced-keys --keep
echo "GAUNTLET GREEN"
