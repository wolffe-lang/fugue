#!/usr/bin/env python3
"""notes/fg04-evidence/measure.py — which side is wrong: the row or the game.

    python3 -I measure.py run --tree TREE --bin BIN --rows a,b --out DIR [--instrument]
    python3 -I measure.py analyse DIR

`run` loads TREE's own engine runner (`.lair/tools/pty`, by path) and TREE's
own rows (`tests/pty_rows.py`, by path) and runs the named rows UNCHANGED,
with one difference: the runner's `Session` records every session. Each
session's argv, every write to its pty (monotonic time and bytes), every
read of its pty and of its stderr (time, cumulative length), its whole
output and stderr and its `--record` file land in DIR/<row>/<n>/. With
--instrument, a session whose argv runs the game directly (stderr on its own
pipe) and lacks `--trace`/`--record` gets them, so its ticks can be read;
a session whose stderr shares the terminal is never touched. The row's own
verdict (its `pty: ... ok/FAILED` line) is printed as the runner prints it.

`analyse` judges every session that has a trace and a recording:
  - the game against its own record: every carrying frame, cut at its exact
    output boundary (`trace output frame F bytes N`), applied by the game's
    terminal model, must equal the headless replay of the game's own
    recording at that tick (glyphs and styles): `game-agrees`;
  - the key mapping: each recorded key belongs to the first carrying frame
    after its record tick; `due` is that frame's tick less the key's;
  - the row's two attributions, re-measured: the frames trunk's rows read
    as `tick-1` (a key at T matched only to a frame at T+1) and the bytes a
    row held when it read a trace line (`snapshot` against the boundary).
It writes DIR/<row>/<n>/analysis.json and DIR/summary.json and prints one
line a session. Nothing here sends a signal or touches the game's code.
"""
import argparse, glob, importlib.machinery, importlib.util, json, os, re, shutil, subprocess, sys, time

OUT_RE = re.compile(rb'trace output frame (\d+) bytes (\d+)\n')
KEY_RE = re.compile(rb'trace frame (\d+) carries_key inner_us (\d+)\n')


def load_runner(tree):
    path = os.path.join(tree, '.lair', 'tools', 'pty')
    loader = importlib.machinery.SourceFileLoader('lair_pty_measured', path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader('lair_pty_measured', loader))
    loader.exec_module(mod)
    return mod


def run(args):
    runner = load_runner(os.path.abspath(args.tree))
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    masters = {}          # fd -> session log
    errs = {}             # fd -> session log
    real_write, real_read = os.write, os.read

    def write(fd, data):
        log = masters.get(fd)
        if log is not None:
            log['writes'].append([time.monotonic(), bytes(data).hex()])
        return real_write(fd, data)

    def read(fd, n):
        chunk = real_read(fd, n)
        log = masters.get(fd)
        if log is not None:
            log['out_len'] += len(chunk)
            log['out_reads'].append([time.monotonic(), log['out_len']])
        log = errs.get(fd)
        if log is not None:
            log['err_len'] += len(chunk)
            log['err_reads'].append([time.monotonic(), log['err_len']])
        return chunk

    os.write, os.read = write, read
    state = {'row': None, 'n': 0}

    class Recorded(runner.Session):
        def __init__(self, argv, *rest, **kw):
            argv = list(argv)
            direct = os.path.basename(argv[0]) == os.path.basename(args.bin) or argv[0] == args.bin
            state['n'] += 1
            self.measure_dir = os.path.join(out, state['row'], '%03d' % state['n'])
            os.makedirs(self.measure_dir, exist_ok=True)
            added = []
            if args.instrument and direct:
                if '--trace' not in argv:
                    argv.append('--trace'); added.append('--trace')
                if '--record' not in argv and '--replay' not in argv and '--script' not in argv:
                    argv += ['--record', os.path.join(self.measure_dir, 'record.pk')]; added.append('--record')
            self.measure_log = {'argv': argv, 'added': added, 'direct': direct, 'start': time.monotonic(),
                                'writes': [], 'out_reads': [], 'err_reads': [], 'out_len': 0, 'err_len': 0}
            self._measure_registered = False
            super().__init__(argv, *rest, **kw)

        def pump(self, seconds):
            if not self._measure_registered and hasattr(self, 'master'):
                masters[self.master] = self.measure_log
                errs[self.r_err] = self.measure_log
                self._measure_registered = True
            return super().pump(seconds)

        def finish(self, timeout=30.0):
            try:
                return super().finish(timeout)
            finally:
                self.measure_save()

        def measure_save(self):
            log = self.measure_log
            log['end'] = time.monotonic()
            log['status'] = getattr(self, 'status', None)
            d = self.measure_dir
            open(os.path.join(d, 'out.bin'), 'wb').write(self.out)
            open(os.path.join(d, 'err.bin'), 'wb').write(self.err)
            argv = log['argv']
            if '--record' in argv:
                src = argv[argv.index('--record') + 1]
                if os.path.exists(src) and os.path.abspath(src) != os.path.join(d, 'record.pk'):
                    shutil.copy(src, os.path.join(d, 'record.pk'))
            json.dump(log, open(os.path.join(d, 'session.json'), 'w'))
            masters.pop(getattr(self, 'master', -1), None)
            errs.pop(getattr(self, 'r_err', -1), None)

    # The Session's constructor pumps before any override can register the
    # fds, so register on the first pump (above) and also wrap pty.openpty's
    # result through the constructor: the first pump happens inside it.
    runner.Ctx.Session = Recorded
    runner.Session = Recorded
    rows = runner.game_rows()
    names = args.rows.split(',')
    verdicts = {}
    for name in names:
        state['row'], state['n'] = name, 0
        try:
            s, problems = rows[name](os.path.abspath(args.bin), runner.Ctx)
        except Exception as e:
            print('pty: %s FAILED: %s' % (name, e), flush=True)
            verdicts[name] = ['exception: %s' % e]
            continue
        verdicts[name] = problems
        if problems:
            print('pty: %s FAILED (%s %s):' % (name, sys.platform, os.uname().machine), flush=True)
            for p in problems:
                print('  - ' + p, flush=True)
        else:
            print('pty: %s ok (%s %s, exit %d)' % (name, sys.platform, os.uname().machine, s.status), flush=True)
    json.dump(verdicts, open(os.path.join(out, 'verdicts.json'), 'w'), indent=2)
    os.write, os.read = real_write, real_read
    return 1 if any(verdicts.values()) else 0


def arg_value(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def applied(binary, data, size, scratch):
    path = os.path.join(scratch, 'frame.bin')
    open(path, 'wb').write(data)
    r = subprocess.run([binary, '--apply', path, '--size', size], capture_output=True, timeout=60)
    if r.returncode:
        return None
    text, styles, _ = r.stdout.decode().split('--\n')
    return text, styles


def analyse_session(d, binary):
    log = json.load(open(os.path.join(d, 'session.json')))
    argv = log['argv']
    out = open(os.path.join(d, 'out.bin'), 'rb').read()
    err = open(os.path.join(d, 'err.bin'), 'rb').read()
    record = os.path.join(d, 'record.pk')
    if '--trace' not in argv or not os.path.exists(record):
        return None
    binary = binary or argv[0]
    outputs = [(int(t), int(n)) for t, n in OUT_RE.findall(err)]
    carrying = [int(t) for t, _ in KEY_RE.findall(err)]
    inner = {int(t): int(u) for t, u in KEY_RE.findall(err)}
    keys = []
    for line in open(record).read().splitlines():
        w = line.split()
        if len(w) >= 3 and w[0] == 't':
            keys.append((int(w[1]), w[2]))
    size = '%sx%s' % tuple(arg_value(argv, '--size', '80x24').split('x'))
    entry = out.find(b'\x1b[1;1H')
    result = {'dir': d, 'argv': argv, 'keys': len(keys), 'carrying_frames': len(carrying),
              'entry': entry, 'frames': []}
    if entry < 0 or not outputs:
        result['error'] = 'no frame boundary'
        return result
    boundary = dict(outputs)
    # Each key belongs to the first carrying frame after its record tick.
    by_frame = {}
    unmapped = []
    for i, (t, k) in enumerate(keys):
        f = next((c for c in carrying if c > t), None)
        if f is None:
            if k != 'quit':
                unmapped.append(i)
            continue
        by_frame.setdefault(f, []).append((i, t, k))
    scratch = os.path.join(d, 'analyse-tmp')
    os.makedirs(scratch, exist_ok=True)
    last = max(carrying) if carrying else 0
    hd = os.path.join(scratch, 'replay')
    if os.path.exists(hd):
        shutil.rmtree(hd)
    r = subprocess.run([binary, '--headless', '--script', record, '--frames', str(last + 1), '--every', '1',
                        '--dump', hd, '--mute'], capture_output=True, timeout=600)
    if r.returncode:
        result['error'] = 'headless replay failed: %r' % r.stderr[-300:]
    # The row's snapshot when it read each carrying trace: the bytes it held.
    err_reads = log.get('err_reads', [])
    out_reads = log.get('out_reads', [])
    def held_at(err_offset):
        when = next((t for t, n in err_reads if n >= err_offset), None)
        if when is None:
            return None, None
        held = max((n for t, n in out_reads if t <= when), default=0)
        return when, held
    agree = disagree = 0
    for m in KEY_RE.finditer(err):
        f = int(m.group(1))
        n = boundary.get(f)
        frame = {'frame': f, 'keys': [k for _, _, k in by_frame.get(f, [])],
                 'record_ticks': sorted({t for _, t, _ in by_frame.get(f, [])}),
                 'inner_us': inner.get(f), 'boundary': None if n is None else entry + n}
        frame['due'] = (f - frame['record_ticks'][0]) if frame['record_ticks'] else None
        frame['tick_minus_one_keys'] = sum(1 for t, _ in keys if t == f - 1)
        when, held = held_at(m.end())
        frame['row_snapshot'] = held
        frame['snapshot_ahead_bytes'] = None if held is None or n is None else held - (entry + n)
        if n is not None and r.returncode == 0:
            live = applied(binary, out[:entry + n], size, scratch)
            base = os.path.join(hd, 'frame-%04d' % (f - 1))
            want = (open(base + '.txt').read(), open(base + '.sty').read()) if os.path.exists(base + '.txt') else None
            frame['game_agrees'] = live is not None and want is not None and live == want
            if frame['game_agrees']:
                agree += 1
            else:
                disagree += 1
                frame['live_text_rows_differ'] = None if live is None or want is None else \
                    [i for i, (a, b) in enumerate(zip(live[0].splitlines(), want[0].splitlines())) if a != b][:6]
        result['frames'].append(frame)
    shutil.rmtree(scratch, ignore_errors=True)
    result['game_agrees'] = agree
    result['game_disagrees'] = disagree
    result['unmapped_keys'] = unmapped
    result['catch_up_frames'] = sum(1 for fr in result['frames'] if fr['due'] and fr['due'] > 1)
    result['coalesced_frames'] = sum(1 for fr in result['frames'] if len(fr['keys']) > 1)
    result['row_unaccounted_keys'] = sum(len(fr['keys']) for fr in result['frames'] if fr['tick_minus_one_keys'] == 0)
    result['snapshot_ahead_frames'] = sum(1 for fr in result['frames']
                                          if fr['snapshot_ahead_bytes'] and fr['snapshot_ahead_bytes'] > 0
                                          and any(b > fr['boundary'] and b <= fr['row_snapshot']
                                                  for b in [entry + x for _, x in outputs]
                                                  if fr['boundary'] is not None and x is not None and
                                                  entry + x != fr['boundary']))
    # Host stall as the game saw it: a carrying wake's catch-up beyond one tick.
    result['max_due'] = max((fr['due'] or 0 for fr in result['frames']), default=0)
    result['max_inner_ms'] = max((fr['inner_us'] or 0 for fr in result['frames']), default=0) / 1000
    json.dump(result, open(os.path.join(d, 'analysis.json'), 'w'), indent=1)
    return result


def analyse(args):
    out = os.path.abspath(args.dir)
    summary = []
    for d in sorted(glob.glob(os.path.join(out, '*', '[0-9][0-9][0-9]'))):
        try:
            r = analyse_session(d, args.bin)
        except Exception as e:
            r = {'dir': d, 'error': 'analysis failed: %s' % e}
        if r is None:
            continue
        row = os.path.basename(os.path.dirname(d))
        line = {k: r.get(k) for k in ('keys', 'carrying_frames', 'game_agrees', 'game_disagrees', 'unmapped_keys',
                                      'catch_up_frames', 'coalesced_frames', 'row_unaccounted_keys',
                                      'snapshot_ahead_frames', 'max_due', 'max_inner_ms', 'error')}
        line['row'] = row
        line['session'] = os.path.basename(d)
        summary.append(line)
        print('%s/%s: keys %s frames %s game agrees %s disagrees %s; catch-up %s coalesced %s max due %s '
              'max inner %.1f ms; trunk-unaccounted %s snapshot-ahead %s%s' % (
                  row, line['session'], line['keys'], line['carrying_frames'], line['game_agrees'],
                  line['game_disagrees'], line['catch_up_frames'], line['coalesced_frames'], line['max_due'],
                  line['max_inner_ms'] or 0, line['row_unaccounted_keys'], line['snapshot_ahead_frames'],
                  (' ERROR ' + line['error']) if line.get('error') else ''), flush=True)
    json.dump(summary, open(os.path.join(out, 'summary.json'), 'w'), indent=1)
    total = sum(s['game_disagrees'] or 0 for s in summary)
    print('measure: %d sessions, %d frames the game disagrees with its own record' % (len(summary), total))
    return 1 if total else 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--tree', required=True)
    r.add_argument('--bin', required=True)
    r.add_argument('--rows', required=True)
    r.add_argument('--out', required=True)
    r.add_argument('--instrument', action='store_true')
    a = sub.add_parser('analyse')
    a.add_argument('dir')
    a.add_argument('--bin')
    args = ap.parse_args()
    return run(args) if args.cmd == 'run' else analyse(args)


if __name__ == '__main__':
    sys.exit(main())
