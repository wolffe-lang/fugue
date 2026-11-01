#!/usr/bin/env python3
"""notes/fg04-evidence/stall.py — the forced stall for fg04's measurements and proof.

    taskpolicy -c background python3 -I notes/fg04-evidence/stall.py --load N -- CMD ...

A copy of pack's notes/pk09-evidence/stall.py (pk09, R-pk09-4), renamed. It
starts N busy processes, runs CMD and waits for it, then stops the load and
waits for every busy process: the exit status is CMD's. A busy process spins
until a stop file appears (or a 30-minute ceiling passes), so nothing here
sends a signal. Run under `taskpolicy -c background`, CMD (the pty runner and
the game it starts) and the load share macOS's background QoS clamp, the
lowest scheduling class it has, so the load competes with the game and the row
first. The Mac has no CPU-affinity call; this stands in for cb19's busy loops
on the row's CPU (stress4: 2 and 3 loops). The note gives the stalls it
produced as measured (the rows' own stall probe and the game's catch-up
wakes), never assumed. N = 0 runs CMD in the clamp with no load.
"""
import argparse, os, subprocess, sys, tempfile, time

CEILING_S = 1800


def spinner(stop):
    code = ("import os, time\nend = time.monotonic() + %d\nn = 0\n"
            "while time.monotonic() < end:\n    n += 1\n"
            "    if n %% 200000 == 0 and os.path.exists(%r):\n        break\n") % (CEILING_S, stop)
    return subprocess.Popen([sys.executable, "-I", "-c", code])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", type=int, required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command")
    d = tempfile.mkdtemp(prefix="fg04-stall-")
    stop = os.path.join(d, "stop")
    load = [spinner(stop) for _ in range(a.load)]
    t0 = time.monotonic()
    try:
        rc = subprocess.run(cmd).returncode
    finally:
        open(stop, "w").close()
        for p in load:
            p.wait()
        os.unlink(stop)
        os.rmdir(d)
    print("stall: load %d, %.0f s, the command's exit %d" % (a.load, time.monotonic() - t0, rc), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
