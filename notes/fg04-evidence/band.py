#!/usr/bin/env python3
"""notes/fg04-evidence/band.py — how many cores macOS's background QoS band gives.

    taskpolicy -c background python3 -I notes/fg04-evidence/band.py [MAX]

For k = 1..MAX (default 10), starts k busy processes in the caller's
scheduling class (run it in the clamp), lets each count loop iterations for
2 s and print its count, and reports each one's throughput against k = 1's.
Where k passes the band's cores, the per-process throughput falls as C/k.
Each process stops at its own deadline: nothing here sends a signal.
"""
import subprocess, sys, time

CODE = ("import time\nend = time.monotonic() + 2.0\nn = 0\n"
        "while time.monotonic() < end:\n    n += 1\nprint(n)\n")


def run(k):
    procs = [subprocess.Popen([sys.executable, '-I', '-c', CODE], stdout=subprocess.PIPE, text=True) for _ in range(k)]
    return [int(p.communicate()[0]) for p in procs]


def main():
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    base = None
    for k in range(1, top + 1):
        counts = run(k)
        mean = sum(counts) / k
        base = base or mean
        print('band: k=%2d per-process %.2f of k=1, total %.2f cores' % (k, mean / base, sum(counts) / base), flush=True)
        time.sleep(1)


if __name__ == '__main__':
    main()
