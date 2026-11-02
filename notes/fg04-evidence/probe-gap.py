#!/usr/bin/env python3
"""notes/fg04-evidence/probe-gap.py — how long a stall probe takes to start.

    python3 -I probe-gap.py [N]

`tests/paced.py`'s StallProbe is a Python process the rows start just before
the window it vouches for (`audition-hear-owner` starts it, then writes h at
once). The probe sees only the ticks after its own start, so the window's
first part, before the probe runs, is unmeasured, and its silence there says
nothing about the host. This times that gap the way a row meets it: from the
`Popen` to the first moment the probe's own script runs (the probe's imports
done, `time.monotonic()` read, the clock every process shares), N times
(default 20), spaced by a poll(2) wait (not coalesced in the clamp). Prints
one line a start, then the min, median and max in ms.
"""
import select, statistics, subprocess, sys, time

CHILD = 'import os, select, sys, time\nsys.stdout.write("%.6f\\n" % time.monotonic()); sys.stdout.flush()\nsys.stdin.read()\n'


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    gaps = []
    waiter = select.poll()
    for i in range(n):
        began = time.monotonic()
        p = subprocess.Popen([sys.executable, '-I', '-c', CHILD], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        started = float(p.stdout.readline())
        p.stdin.close(); p.wait()
        gaps.append((started - began) * 1000)
        print(f'probe-gap: start {i + 1}: the probe ran {gaps[-1]:.3f} ms after its Popen', flush=True)
        waiter.poll(250)
    print(f'probe-gap: {n} starts: min {min(gaps):.3f} ms, median {statistics.median(gaps):.3f} ms, '
          f'max {max(gaps):.3f} ms', flush=True)


if __name__ == '__main__':
    main()
