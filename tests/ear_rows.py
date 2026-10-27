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
                    elif chunk: self.err += chunk
    return Prompt


def setup(binary, ctx, name, mute=False):
    root = Path(ctx.ROOT)/'target/pty'/name
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True)
    env = ctx.env_for()
    env.update(FUGUE_SOUND='1', FUGUE_AUDIO_TRACE='0', FUGUE_WAV_DIR=str(root),
               FUGUE_STATE=str(root/'state'), TMPDIR=os.environ.get('TMPDIR', str(root)))
    args = [binary, '--book', '5', '--seed', '7', '--no-title', '--size', '120x40',
            '--record', str(root/'record.pk')] + (['--mute'] if mute else [])
    s = session_type(ctx)(['/bin/sh', '-c', 'exec "$@" 2>&1', 'ear-row']+args, 40, 120, env)
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
    s, root = setup(binary,ctx,'audition-storm')
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
    # Analyse read snapshots after sending, never run terminal models in the
    # timed loop. Preserve every distinct valid state even when two writes
    # arrive close together; only an incomplete split write may wait <=4 ms
    # for its completing read.
    presses, extra, captures = [], [], []
    previous = natural
    pending = None
    for at,capture in s.reads:
        actual = image(binary,root,capture)
        valid = actual in (natural,sharp)
        if not valid:
            if pending is None: pending = (at,capture,actual)
            continue
        if pending is not None:
            if at-pending[0]>.004:
                a,sa = cells(pending[2])
                delta = min(changed(a,cells(state)[0]) for state in (natural,sharp))
                extra.append(delta)
                problems.append(f'terminal held an unexpected state for {(at-pending[0])*1000:.3f} ms ({delta} text cells)')
            pending = None
        if actual == previous: continue
        index = len(presses)
        presses.append(dict(press=index+1,wall_ms=None if index>=len(sent) else (at-sent[index])*1000))
        extra.append(0)
        previous = actual
        captures.append(capture)
        (root/f'frame-{len(captures):02}.bin').write_bytes(capture)
    if pending is not None:
        a,sa = cells(pending[2])
        delta = min(changed(a,cells(state)[0]) for state in (natural,sharp))
        extra.append(delta)
        problems.append(f'player left an unexpected terminal state ({delta} text cells)')
    final = image(binary,root,s.out)
    if final != natural: problems.append('forty recorded toggles did not restore the exact initial frame')
    alive = max([len(p['pids']) for p in polls], default=0)
    if is_mac and (not polls or alive == 0): problems.append('storm never observed a real player')
    if alive > 1: problems.append(f'audition children alive: {alive}, wanted <=1')
    latencies = [p['wall_ms'] for p in presses if p['wall_ms'] is not None]
    # Ordered state changes correspond one-to-one to presses only when all
    # forty were drawn. Never publish a shifted, fabricated per-key p99 for
    # a coalesced/missing intermediate state.
    p99 = sorted(latencies)[math.ceil(len(latencies)*.99)-1] if len(latencies)==40 else None
    if is_mac and len(latencies)!=40: problems.append(f'only {len(latencies)}/40 presses produced a distinct expected frame')
    if is_mac and p99 is None: problems.append('per-press p99 unavailable without forty expected frames')
    elif is_mac and (p99>70 or min(latencies)<0): problems.append(f'storm p99 latency {p99} ms exceeds 70 ms or frame preceded its press')
    if b'AudioQueueStart' in s.out or b'Error:' in s.out: problems.append('player error reached terminal during storm')
    sinks = list(root.glob('audition*.wav'))
    if not is_mac and len(sinks)!=1: problems.append(f'Linux audition sink grew to {len(sinks)} files, wanted one rewritten file')
    if not is_mac and (not sinks or sinks[0].read_bytes() != (root/'note-21-0.wav').read_bytes()):
        problems.append('Linux sink did not retain the final natural C3 WAV intact')
    s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
    recorded = [line for line in (root/'record.pk').read_text().splitlines() if line.endswith(' sharp')]
    if len(recorded)!=40: problems.append(f'recording has {len(recorded)}/40 sharp keys')
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
