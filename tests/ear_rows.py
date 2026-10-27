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
        def pump(self, seconds):
            end = time.monotonic() + seconds
            while time.monotonic() < end:
                fds = [self.r_err] + ([] if self.eof else [self.master])
                ready, _, _ = select.select(fds, [], [], min(.002, max(0, end-time.monotonic())))
                for fd in ready:
                    try: chunk = os.read(fd, 65536)
                    except OSError: chunk = b''
                    if fd == self.master:
                        if chunk: self.out += chunk
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
    # Seed 7 is Dorian. Walk to the final event, then one whole back to
    # the penultimate event. Its seventh is C; C3 is inside the bass bank.
    s.type(b'\x1b[C'*200, .15)
    s.type(b'\x1b[D'*8, .15)
    screen = image(binary, root, s.out).decode().split('--\n')[0].splitlines()
    label = screen[8][98:].strip()
    match = re.match(r'([A-G])([#b]?)([0-9])', label)
    if not match: raise RuntimeError('cannot read selected pitch: '+label)
    pos = int(match[3])*7 + 'CDEFGAB'.index(match[1])
    target = 21
    s.type((b'\x1b[A' if pos < target else b'\x1b[B')*abs(target-pos), .15)
    s.pump(1.2)  # setup players have ended before the measured storm


def storm(binary, ctx):
    problems = []
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
    polls, presses, captures = [], [], []
    start = time.monotonic()
    for index in range(40):
        sent = time.monotonic(); size = len(s.out)
        os.write(s.master,b'#')
        first = None
        deadline = start+(index+1)*.05
        while time.monotonic() < deadline:
            s.pump(.002)
            if first is None and len(s.out)>size: first = time.monotonic()
            if Path('/usr/bin/afplay').exists():
                pids = children(s)
                polls.append(dict(at_ms=(time.monotonic()-start)*1000,pids=pids))
        captures.append(s.out)
        presses.append(dict(press=index+1,wall_ms=None if first is None else (first-sent)*1000))
    s.pump(.15)
    # Retain and analyse after the timed presses: applying 40 terminal models
    # during the storm would itself change the workload being measured.
    extra = []
    for index,capture in enumerate(captures):
        actual = image(binary,root,capture)
        expected = sharp if index%2==0 else natural
        a, sa = cells(actual); b, sb = cells(expected)
        delta = changed(a,b); style_delta = changed(sa,sb)
        extra.append(delta)
        if delta or style_delta: problems.append(f'press {index+1}: {delta} unexpected text cells / {style_delta} style rows')
        (root/f'press-{index+1:02}.bin').write_bytes(capture)
    alive = max([len(p['pids']) for p in polls], default=0)
    is_mac = Path('/usr/bin/afplay').exists()
    if is_mac and (not polls or alive == 0): problems.append('storm never observed a real player')
    if alive > 1: problems.append(f'audition children alive: {alive}, wanted <=1')
    latencies = [p['wall_ms'] for p in presses if p['wall_ms'] is not None]
    p99 = sorted(latencies)[math.ceil(len(latencies)*.99)-1] if latencies else None
    if len(latencies)!=40: problems.append(f'only {len(latencies)}/40 presses produced a frame')
    if p99 is None or p99>70: problems.append(f'storm p99 latency {p99} ms exceeds 70 ms')
    if b'AudioQueueStart' in s.out or b'Error:' in s.out: problems.append('player error reached terminal during storm')
    sinks = list(root.glob('audition*.wav'))
    if not is_mac and len(sinks)!=1: problems.append(f'Linux audition sink grew to {len(sinks)} files, wanted one rewritten file')
    s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
    recorded = [line for line in (root/'record.pk').read_text().splitlines() if line.endswith(' sharp')]
    if len(recorded)!=40: problems.append(f'recording has {len(recorded)}/40 sharp keys')
    result = dict(children_alive_max=alive,p99_ms=p99,presses=presses,polls=polls,
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


ROWS = {'quiet-player-stderr':quiet_failure, 'audition-storm':storm}
