"""Live sound-owner witnesses: real players, merged stderr and exact cells."""
import json
import math
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import time


# The ordinary pty runner waits 20 ms per read. Retain its terminal ownership
# and restore checks, but read promptly enough to measure a 20 Hz storm.
def session_type(ctx):
    class Prompt(ctx.Session):
        def __init__(self, *args):
            self.reads = []
            self.capture_reads = False
            self.trace_reads = []
            super().__init__(*args)

        def pump(self, seconds):
            end = time.monotonic() + seconds
            while time.monotonic() < end:
                fds = [self.r_err] + ([] if self.eof else [self.master])
                ready, _, _ = select.select(fds, [], [], min(.002, max(0, end-time.monotonic())))
                for fd in ready:
                    try: chunk = os.read(fd, 65536)
                    except OSError: chunk = b''
                    if fd == self.master:
                        if chunk:
                            self.out += chunk
                            if self.capture_reads: self.reads.append((time.monotonic(), self.out))
                        else: self.eof = True
                    elif chunk:
                        self.err += chunk
                        if self.capture_reads: self.trace_reads.append((time.monotonic(), self.err))
    return Prompt


def setup(binary, ctx, name, mute=False, trace=False):
    root = Path(ctx.ROOT)/'target/pty'/name
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True)
    env = ctx.env_for()
    env.update(FUGUE_SOUND='1', FUGUE_AUDIO_TRACE='0', FUGUE_WAV_DIR=str(root),
               FUGUE_STATE=str(root/'state'), TMPDIR=os.environ.get('TMPDIR', str(root)))
    args = [binary, '--book', '5', '--seed', '7', '--no-title', '--size', '120x40',
            '--record', str(root/'record.pk')] + (['--mute'] if mute else [])
    if trace:
        args.append('--trace')
        argv = args
    else:
        argv = ['/bin/sh', '-c', 'exec "$@" 2>&1', 'ear-row']+args
    s = session_type(ctx)(argv, 40, 120, env)
    deadline = time.monotonic()+30
    while b'\x1b[?1049h' not in s.out and time.monotonic() < deadline: s.pump(.02)
    s.pump(.15)
    if b'\x1b[?1049h' not in s.out: raise RuntimeError('sound preparation never entered terminal')
    return s, root


def image(binary, root, data):
    path = root/'apply.bin'; path.write_bytes(data)
    return subprocess.run([binary, '--apply', str(path), '--size', '120x40'],
                          capture_output=True, check=True).stdout


def cells(applied):
    # --apply emits text then styles. Compare both, including blank cells.
    text, styles = applied.decode().split('--\n', 1)
    return list(text), styles.splitlines()


def changed(a, b):
    return sum(x != y for x, y in zip(a, b)) + abs(len(a)-len(b))


def children(s):
    p = subprocess.run(['pgrep', '-P', str(s.job)], capture_output=True, text=True)
    if p.returncode not in (0, 1): raise RuntimeError('pgrep failed: '+p.stderr)
    return [int(pid) for pid in p.stdout.split()]


def quiet_failure(binary, ctx):
    if not Path('/usr/bin/afplay').exists():
        print('SKIP quiet-player-stderr: macOS afplay required; Linux has its own sink row')
        return quiet_sink(binary, ctx)
    problems = []
    s, root = setup(binary, ctx, 'quiet-player-stderr')
    before = image(binary, root, s.out)
    bank = list(root.glob('note-*.wav'))
    if not bank: problems.append('prepared note bank absent')
    # Fault the real input, not the program or executable: spawn still succeeds,
    # afplay itself must diagnose this empty WAV. Space makes no editor change.
    for path in bank: path.write_bytes(b'')
    s.type(b' ', .7)
    after = image(binary, root, s.out)
    a, sa = cells(before); b, sb = cells(after)
    delta = changed(a,b); style_delta = changed(sa,sb)
    if delta or style_delta: problems.append(f'player stderr changed {delta} text cells / {style_delta} style rows')
    if b'Error:' in s.out or b'AudioQueueStart' in s.out: problems.append('afplay diagnostic reached the terminal')
    alive = children(s)
    if alive: problems.append('failed player remained alive after .7 seconds')
    s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
    result = dict(text_cells_changed=delta, style_rows_changed=style_delta, alive=alive)
    (root/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    print('quiet-player-stderr: '+json.dumps(result))
    return s, problems


def cadence(s, binary, root):
    # Seed 7 is Dorian. Walk to the final event, then one event back to
    # the penultimate event. Its seventh is C; C3 is inside the bass bank.
    s.type(b'\x1b[C'*200, .15)
    s.type(b'\x1b[D', .15)
    screen = image(binary, root, s.out).decode().split('--\n')[0].splitlines()
    if 'Bar 9, beat 5:8' not in screen[5]:
        raise RuntimeError('cadence setup did not select the penultimate event: '+screen[5])
    label = screen[8][98:].strip()
    match = re.match(r'([A-G])([#b]?)([0-9])', label)
    if not match: raise RuntimeError('cannot read selected pitch: '+label)
    pos = int(match[3])*7 + 'CDEFGAB'.index(match[1])
    target = 21
    s.type((b'\x1b[A' if pos < target else b'\x1b[B')*abs(target-pos), .15)
    s.pump(1.2)  # setup players have ended before the measured storm


def storm(binary, ctx):
    problems = []
    is_mac = Path('/usr/bin/afplay').exists()
    # An independent muted run supplies the only two permitted full frames.
    # This covers pitch/interval/judge text as well as the accidental itself;
    # no arbitrary region is masked to hide a child diagnostic.
    ref, rr = setup(binary, ctx, 'audition-reference', mute=True)
    cadence(ref,binary,rr)
    natural = image(binary,rr,ref.out)
    ref.type(b'#',.10); sharp = image(binary,rr,ref.out)
    ref.type(b'#',.10); restored = image(binary,rr,ref.out)
    if natural == sharp or natural != restored: problems.append('cadence fixture did not alternate two distinct spellings')
    ref.type(b'q'); ref.finish(); ctx.common_checks(ref,0,problems)
    s, root = setup(binary,ctx,'audition-storm',trace=True)
    cadence(s,binary,root)
    initial = image(binary,root,s.out)
    if initial != natural: problems.append('live and muted initial frames differ')
    polls, sent = [], []
    s.capture_reads = True
    start = time.monotonic()
    for index in range(40):
        sent.append(time.monotonic())
        os.write(s.master,b'#')
        deadline = start+(index+1)*.05
        while time.monotonic() < deadline:
            s.pump(.002)
            if is_mac:
                pids = children(s)
                polls.append(dict(at_ms=(time.monotonic()-start)*1000,pids=pids))
    # The key interval is 50 ms but the frame budget is 70 ms. Capture
    # independently of send slots so a legal late frame belongs to its
    # actual press, not the following press. Final reads get the same budget.
    send_span_ms = (sent[-1]-sent[0])*1000
    if send_span_ms > 2000: problems.append(f'forty presses took {send_span_ms:.3f} ms, over two seconds')
    s.pump(.10)
    s.capture_reads = False
    measured = s.out
    # Analyse successful write prefixes, never terminal-read chunk boundaries.
    import runpy
    checker = runpy.run_path(str(Path(__file__).with_name('storm_frames.py')))['carrying_frames']
    # Recording is the independent ordered input journal. Trace supplies only
    # successful byte-write boundaries; never a claimed pitch or verdict.
    s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
    recorded = [int(line.split()[1]) for line in (root/'record.pk').read_text().splitlines() if line.endswith(' sharp')]
    entry = s.out.index(b'\x1b[1;1H')
    presses, errors = checker(recorded, s.err, s.out, entry,
                              lambda data: image(binary,root,data), natural, sharp)
    problems.extend(errors)
    extra = [0 if p['correct'] else 1 for p in presses]
    for p in presses:
        arrived = next((at for at,data in s.reads if len(data)>=p['output_bytes']), None)
        marker = f"trace output frame {p['frame']} bytes {p['output_bytes']-entry}\n".encode()
        traced = next((at for at,data in s.trace_reads if marker in data), None)
        # An unchanged (even-parity) batch still needs a completed frame trace.
        completed = max(at for at in (arrived,traced) if at is not None) if arrived is not None or traced is not None else None
        p['wall_ms'] = (completed-sent[p['press']-1])*1000 if completed is not None else None
        (root/f"frame-{p['press']:02}.bin").write_bytes(s.out[:p['output_bytes']])
    (root/'trace.err').write_bytes(s.err)
    (root/'complete.bin').write_bytes(s.out)
    final = image(binary,root,measured)
    if final != natural: problems.append('forty recorded toggles did not restore the exact initial frame')
    alive = max([len(p['pids']) for p in polls], default=0)
    if is_mac and (not polls or alive == 0): problems.append('storm never observed a real player')
    if alive > 1: problems.append(f'audition children alive: {alive}, wanted <=1')
    latencies = [p['wall_ms'] for p in presses if p['wall_ms'] is not None]
    # Ordered state changes correspond one-to-one to presses only when all
    # forty were drawn. Never publish a shifted, fabricated per-key p99 for
    # a coalesced/missing intermediate state.
    p99 = sorted(latencies)[math.ceil(len(latencies)*.99)-1] if len(latencies)==40 else None
    if len(latencies)!=40: problems.append(f'only {len(latencies)}/40 presses have an exact correct carrying frame')
    if p99 is None: problems.append('per-press p99 unavailable without forty accounted presses')
    elif is_mac and (p99>70 or min(latencies)<0): problems.append(f'storm p99 latency {p99} ms exceeds 70 ms or frame preceded its press')
    if b'AudioQueueStart' in s.out or b'Error:' in s.out: problems.append('player error reached terminal during storm')
    sinks = list(root.glob('audition*.wav'))
    if not is_mac and len(sinks)!=1: problems.append(f'Linux audition sink grew to {len(sinks)} files, wanted one rewritten file')
    if not is_mac and (not sinks or sinks[0].read_bytes() != (root/'note-21-0.wav').read_bytes()):
        problems.append('Linux sink did not retain the final natural C3 WAV intact')
    result = dict(children_alive_max=alive,p99_ms=p99,presses=presses,polls=polls,
                  send_span_ms=send_span_ms,observed_frames=len(presses),
                  unexpected_cells_max=max(extra,default=0),unexpected_cells=extra,
                  intentional_text_cells=changed(cells(natural)[0],cells(sharp)[0]),
                  sink_files=len(sinks),recorded=len(recorded))
    (root/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'audition-storm: children max {alive}, p99 {p99} ms, extra cells {max(extra,default=0)}, sink files {len(sinks)}, keys {len(recorded)}/40')
    return s, problems


def quiet_sink(binary, ctx):
    # mac-only rows are loud, but still exercise a valid terminal lifecycle.
    s, _ = setup(binary,ctx,'quiet-sink',mute=True)
    s.type(b'q'); s.finish(); problems=[]; ctx.common_checks(s,0,problems)
    return s,problems


def hear_replaces_audition(binary, ctx):
    problems = []
    s, root = setup(binary,ctx,'audition-hear-owner')
    s.type(b' ',.12)
    previous = children(s)
    if len(previous)!=1: problems.append(f'Space did not start exactly one owned audition: {previous}')
    sent = time.monotonic(); os.write(s.master,b'h')
    retired = False
    while time.monotonic()-sent < .10:
        s.pump(.002)
        if not set(previous).intersection(children(s)):
            retired = True; break
    stopped_ms = (time.monotonic()-sent)*1000
    if not retired: problems.append('h did not kill and reap the audition within 100 ms')
    deadline = time.monotonic()+30
    whole = []
    while time.monotonic()<deadline:
        s.pump(.02)
        for pid in children(s):
            args = subprocess.run(['ps','-p',str(pid),'-o','args='],capture_output=True,text=True).stdout
            if '/usr/bin/afplay' in args and '/whole-' in args: whole.append(pid)
        if whole: break
    if len(set(whole))!=1: problems.append(f'h did not keep its own whole-page player: {whole}')
    s.type(b'q'); s.finish(timeout=20); ctx.common_checks(s,0,problems)
    if children(s): problems.append('teardown left an owned player behind')
    print(f'audition-hear-owner: retired {previous} in {stopped_ms:.3f} ms; whole {whole}')
    (root/'measurements.json').write_text(json.dumps(dict(audition=previous,retired=retired,stop_ms=stopped_ms,whole=whole),indent=2)+'\n')
    return s,problems


# The common gate loads only rows applicable to its actual host: two Mac
# regressions plus a whole-player ownership check, or the Linux sink parity.
ROWS = ({'quiet-player-stderr':quiet_failure, 'audition-storm':storm,
         'audition-hear-owner':hear_replaces_audition} if Path('/usr/bin/afplay').exists()
        else {'linux-audition-sink':storm})
