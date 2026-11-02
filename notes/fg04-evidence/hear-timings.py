#!/usr/bin/env python3
"""notes/fg04-evidence/hear-timings.py — the hear-owner row's own numbers, per run.

    python3 -I hear-timings.py OUTROOT

Reads every OUTROOT/<label>-L<level>-<k>/rows.log, takes each
`audition-hear-owner: retired [...] in R ms (the poll that saw it gone began at
P ms); ...; host stall in the window S ms (session N)` line and the row's
verdict, and prints one line a run and, per label and level, the range of the
poll-begin time P (what the 100 ms is judged on, as trunk judged it), of the
retire time R, the sessions driven, any re-drive or SKIP line, and the
verdicts. Writes OUTROOT/timings.txt.
"""
import collections, glob, os, re, sys

LINE = re.compile(r'audition-hear-owner: retired \[[\d, ]*\] in ([\d.]+) ms \(the poll that saw it gone began at ([\d.]+|None) ms\).*'
                  r'host stall in the window ([\d.]+) ms \(session (\d+)\)')
VERDICT = re.compile(r'^pty: audition-hear-owner (ok|FAILED)')
REDRIVE = 'audition-hear-owner: session '
SKIP = 'SKIP audition-hear-owner latency'


def main():
    root = sys.argv[1]
    out, groups = [], collections.defaultdict(list)
    for d in sorted(glob.glob(os.path.join(root, '*-L*-*'))):
        m = re.match(r'(.+)-L(\d+)-(\d+)$', os.path.basename(d))
        log = os.path.join(d, 'rows.log')
        if not m or not os.path.exists(log):
            continue
        text = open(log, errors='replace').read().splitlines()
        sessions = [tuple(float('nan') if x == 'None' else float(x) for x in LINE.search(l).groups()) for l in text if LINE.search(l)]
        verdict = next((VERDICT.match(l)[1] for l in text if VERDICT.match(l)), 'none')
        redrives = sum(l.startswith(REDRIVE) for l in text)
        skips = sum(l.startswith(SKIP) for l in text)
        if skips: verdict += '+SKIP'
        groups[(m[1], int(m[2]))].append((verdict, sessions))
        shown = '; '.join(f'session {int(n)}: poll began {p:.3f} ms, retired {r:.3f} ms, stall {s:.1f} ms' for r, p, s, n in sessions)
        out.append(f'{m[1]} L{m[2]} run {m[3]}: {verdict}: {shown or "no measurement line"}'
                   + (f'; {redrives} session(s) could not measure' if redrives else ''))
    out.append('')
    for (label, level), runs in sorted(groups.items()):
        verdicts = collections.Counter(v for v, _ in runs)
        last = [s[-1] for _, s in runs if s]
        polls = [p for _, p, _, _ in last]
        retires = [r for r, _, _, _ in last]
        driven = collections.Counter(len(s) for _, s in runs)
        out.append(f'{label} level {level}: {len(runs)} runs; verdicts {dict(sorted(verdicts.items()))}; '
                   f'sessions driven {dict(sorted(driven.items()))}; judged session poll began '
                   f'{min(polls):.3f}-{max(polls):.3f} ms; retired {min(retires):.3f}-{max(retires):.3f} ms'
                   if last else f'{label} level {level}: {len(runs)} runs; no measurement line')
    text = '\n'.join(out) + '\n'
    open(os.path.join(root, 'timings.txt'), 'w').write(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
