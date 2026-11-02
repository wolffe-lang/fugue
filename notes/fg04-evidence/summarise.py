#!/usr/bin/env python3
"""notes/fg04-evidence/summarise.py — tabulate series.sh runs.

    python3 -I summarise.py OUTROOT

Reads every OUTROOT/<label>-L<level>-<k>/rows.log and prints, per label and
level: the runs, the runs red, and for each row how many runs it was red in,
with the first red line of each; then the re-drives the paced rows printed
(`session N out of its case`) and any SCHEDULE line. Writes OUTROOT/summary.txt.
"""
import collections, glob, os, re, sys

ROW = re.compile(r'^pty: (\S+) (ok|FAILED)')


def main():
    root = sys.argv[1]
    runs = collections.defaultdict(list)
    for d in sorted(glob.glob(os.path.join(root, '*-L*-*'))):
        m = re.match(r'(.+)-L(\d+)-(\d+)$', os.path.basename(d))
        if not m or not os.path.exists(os.path.join(d, 'rows.log')):
            continue
        runs[(m[1], int(m[2]))].append((int(m[3]), d))
    out = []
    for (label, level), items in sorted(runs.items()):
        red_runs, row_red, first, redrives, schedule, verdicts = 0, collections.Counter(), {}, [], [], 0
        for k, d in sorted(items):
            lines = open(os.path.join(d, 'rows.log'), errors='replace').read().splitlines()
            red = False
            current = None
            for i, line in enumerate(lines):
                m = ROW.match(line)
                if m:
                    verdicts += 1
                    if m[2] == 'FAILED':
                        red = True
                        row_red[m[1]] += 1
                        detail = next((x.strip() for x in lines[i + 1:i + 3] if x.startswith('  - ')), line)
                        first.setdefault(m[1], 'run %d: %s' % (k, detail[:200]))
                if 'out of its case' in line:
                    redrives.append('run %d: %s' % (k, line.strip()[:200]))
                if 'SCHEDULE' in line:
                    schedule.append('run %d: %s' % (k, line.strip()[:200]))
            red_runs += red
        out.append('%s level %d: %d runs, %d red, %d row verdicts' % (label, level, len(items), red_runs, verdicts))
        for row, n in row_red.most_common():
            out.append('  %-28s red in %d: %s' % (row, n, first[row]))
        out.append('  re-drives: %d' % len(redrives))
        out.extend('    ' + r for r in redrives)
        out.append('  SCHEDULE: %d' % len(schedule))
        out.extend('    ' + r for r in schedule)
    text = '\n'.join(out) + '\n'
    open(os.path.join(root, 'summary.txt'), 'w').write(text)
    print(text, end='')


if __name__ == '__main__':
    main()
