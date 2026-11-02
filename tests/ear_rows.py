"""Live sound-owner witnesses: real players, merged stderr and exact cells.

Keys are typed through tests/paced.py (fg04, fugue#36). A traced session is
paced and acknowledged by the game's own trace; a session whose stderr shares
the terminal cannot carry --trace, so its keys are acknowledged by the exact
replayed frame or by the owned player process they start, each with a
liveness bound, never a fixed settle.
"""
import json
import math
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import time

PACED = runpy.run_path(str(Path(__file__).with_name('paced.py')))
SIZE = '120x40'


def setup(binary, ctx, name, mute=False, trace=False):
    root = Path(ctx.ROOT)/'target/pty'/name
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True)
    env = ctx.env_for()
    env.update(FUGUE_SOUND='1', FUGUE_AUDIO_TRACE='0', FUGUE_WAV_DIR=str(root),
               FUGUE_STATE=str(root/'state'), TMPDIR=os.environ.get('TMPDIR', str(root)))
    args = [binary, '--book', '5', '--seed', '7', '--no-title', '--size', SIZE,
            '--record', str(root/'record.pk')] + (['--mute'] if mute else [])
    if trace:
        s = PACED['session'](ctx)(args + ['--trace'], 40, 120, env)
        s.ready()
    else:
        s = PACED['tracked'](ctx)(['/bin/sh', '-c', 'exec "$@" 2>&1', 'ear-row']+args, 40, 120, env, 0.0)
        PACED['await_state'](s, binary, root, PACED['replayed'](binary, root, PACED['header'](5, SIZE, 'rich', seed=7), [], SIZE),
                             SIZE, name + ' initial page')
    return s, root


def image(binary, root, data):
    path = root/'apply.bin'; path.write_bytes(data)
    return subprocess.run([binary, '--apply', str(path), '--size', SIZE],
                          capture_output=True, check=True).stdout


def cells(applied):
    # --apply emits text then styles. Compare both, including blank cells.
    text, styles = applied.decode().split('--\n', 1)
    return list(text), styles.splitlines()


def changed(a, b):
    return sum(x != y for x, y in zip(a, b)) + abs(len(a)-len(b))


def children(s):
    p = subprocess.run(['pgrep', '-P', str(s.job)], capture_output=True, text=True, timeout=2)
    if p.returncode not in (0, 1): raise RuntimeError('pgrep failed: '+p.stderr)
    return [int(pid) for pid in p.stdout.split()]


def drain(s):
    """Read every byte already on the terminal (and stderr), without waiting."""
    import select
    while True:
        fds = [s.r_err] + ([] if s.eof else [s.master])
        ready, _, _ = select.select(fds, [], [], 0)
        if not ready: return
        before = (len(s.out), len(s.err))
        s.pump(.001)
        if (len(s.out), len(s.err)) == before: return


# The editor's state once a single audition's listening animation is over.
SETTLED_TICKS = 91


def quiet_failure(binary, ctx):
    if not Path('/usr/bin/afplay').exists():
        print('SKIP quiet-player-stderr: macOS afplay required; Linux has its own sink row')
        return quiet_sink(binary, ctx)
    problems = []

    def attempt(n):
        s, root = setup(binary, ctx, 'quiet-player-stderr')
        bank = list(root.glob('note-*.wav'))
        if not bank: problems.append('prepared note bank absent')
        # Fault the real input, not the program or executable: spawn still succeeds,
        # afplay itself must diagnose this empty WAV. Space makes no editor change.
        for path in bank: path.write_bytes(b'')
        s.type(b' ', 0)
        # This session's stderr shares the terminal, so it has no trace, and the
        # failed player can end before any process poll sees it. Right is the
        # acknowledgement: it auditions nothing, and once the exact replayed
        # frame of Space then Right is drawn, Space was read and its player
        # started (keys apply in order). A player diagnostic that reached the
        # terminal keeps that frame from ever being drawn.
        began = time.monotonic()
        s.type(b'\x1b[C', 0)
        head = PACED['header'](5, SIZE, 'rich', seed=7)
        want = PACED['replayed'](binary, root, head, ['sound', 'right'], SIZE)
        seen = []
        try:
            PACED['await_state'](s, binary, root, want, SIZE, 'Space then Right')
            acked = True
        except AssertionError as e:
            problems.append(str(e)); acked = False
        # Space starts the listening animation (state, not sound), so the
        # screen moves on after that frame; the damage check is the replayed
        # state once the animation is over, three seconds of ticks in.
        want = PACED['replayed'](binary, root, head, ['sound', 'right'], SIZE, frames=SETTLED_TICKS)
        try:
            PACED['await_state'](s, binary, root, want, SIZE, 'the settled frame after Space then Right')
        except AssertionError as e:
            problems.append(str(e))
        while time.monotonic() < began + PACED['LIVENESS_S']:
            alive = children(s)
            seen = seen or alive
            if not alive: break
            s.pump(.01)
        gone_s = time.monotonic() - began
        drain(s)
        # Both sides as glyphs and styles alone (the replayed .sty has no
        # --apply tail line).
        after = PACED['applied'](binary, root, s.out, SIZE)
        a, sa = list(want[0]), want[1].splitlines()
        b, sb = list(after[0]), after[1].splitlines()
        delta = changed(a,b); style_delta = changed(sa,sb)
        if delta or style_delta: problems.append(f'player stderr changed {delta} text cells / {style_delta} style rows')
        if b'Error:' in s.out or b'AudioQueueStart' in s.out: problems.append('afplay diagnostic reached the terminal')
        alive = children(s)
        if alive: problems.append(f'failed player remained alive {gone_s:.1f} s after Space')
        s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
        result = dict(text_cells_changed=delta, style_rows_changed=style_delta, alive=alive, seen_alive=seen,
                      acknowledged=acked, gone_after_s=gone_s, session=n)
        (root/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
        print('quiet-player-stderr: '+json.dumps(result))
        return s

    s = PACED['redrive']('quiet-player-stderr', attempt, problems)
    return s, problems


def cadence(s, binary, root):
    # Seed 7 is Dorian. Walk to the final event, then one event back to
    # the penultimate event. Its seventh is C; C3 is inside the bass bank.
    s.send(b'\x1b[C'*200)
    ack = s.send(b'\x1b[D')
    screen = image(binary, root, s.frame(ack['frame'])).decode().split('--\n')[0].splitlines()
    if 'Bar 9, beat 5:8' not in screen[5]:
        raise RuntimeError('cadence setup did not select the penultimate event: '+screen[5])
    label = screen[8][98:].strip()
    match = re.match(r'([A-G])([#b]?)([0-9])', label)
    if not match: raise RuntimeError('cannot read selected pitch: '+label)
    pos = int(match[3])*7 + 'CDEFGAB'.index(match[1])
    target = 21
    if pos != target:
        ack = s.send((b'\x1b[A' if pos < target else b'\x1b[B')*abs(target-pos))
    # Setup players have ended before the measured storm: the old row's 1.2 s
    # of wall time, in the game's ticks.
    s.until(ack['frame'] + 36)


# The storm: forty presses at 20 Hz in the game's own ticks (three presses
# every two ticks), each written once the trace makes it due, without waiting
# for the last one's frame: a late wake reads several and draws them in one
# frame, which the recording accounts for. The storm is delivered when the row
# wrote every press within ROW_LATE_S of the trace making it due; a session in
# which the row itself was held up is out of its case and is driven again.
STORM_TARGETS = [(3 * i) // 2 for i in range(40)]
# A press written within half an audition (0.5 s) of its due tick still lands
# while the press before it sounds: still a storm. (The owner sampler's pgrep
# spawns hold Python's GIL for up to ~20 ms, so the row is never exact.)
ROW_LATE_S = 0.5
LATENCY_MIN = 20


def storm(binary, ctx):
    problems = []
    is_mac = Path('/usr/bin/afplay').exists()
    # An independent muted run supplies the only two permitted full frames.
    # This covers pitch/interval/judge text as well as the accidental itself;
    # no arbitrary region is masked to hide a child diagnostic.
    ref, rr = setup(binary, ctx, 'audition-reference', mute=True, trace=True)
    cadence(ref,binary,rr)
    natural = image(binary,rr,ref.frame())
    sharp = image(binary,rr,ref.frame(ref.send(b'#')['frame']))
    restored = image(binary,rr,ref.frame(ref.send(b'#')['frame']))
    if natural == sharp or natural != restored: problems.append('cadence fixture did not alternate two distinct spellings')
    ref.type(b'q'); ref.finish(); ctx.common_checks(ref,0,problems)
    helpers = runpy.run_path(str(Path(__file__).with_name('storm_frames.py')))

    def attempt(n):
        s, root = setup(binary,ctx,'audition-storm',trace=True)
        cadence(s,binary,root)
        initial = image(binary,root,s.frame())
        if initial != natural: problems.append('live and muted initial frames differ')
        polls = []
        start = time.monotonic()
        sampler = helpers['ChildSampler'](lambda: children(s),start) if is_mac else None
        probe = PACED['StallProbe'](root)
        if sampler is not None: sampler.begin()
        try:
            first = s.tick + 1
            writes = [s.write_at(b'#', first + target) for target in STORM_TARGETS]
            s.settle(writes[0])
        finally:
            probe.stop()
            if sampler is not None:
                sampler.finish()
                polls = sampler.polls
                problems.extend('owner observer: '+error for error in sampler.errors)
        sent = [w['written'] for w in writes]
        row_late = [w['written'] - w['due_seen'] for w in writes if w['due_seen'] is not None]
        measured = s.frame()
        checker = helpers['carrying_frames']
        # Recording is the independent ordered input journal. Trace supplies only
        # successful byte-write boundaries; never a claimed pitch or verdict.
        s.type(b'q'); s.finish(); ctx.common_checks(s,0,problems)
        recorded = [int(line.split()[1]) for line in (root/'record.pk').read_text().splitlines() if line.endswith(' sharp')]
        s.verify(root/'record.pk', 'audition-storm', problems)
        entry = s.entry()
        presses, errors = checker(recorded, s.err, s.out, entry,
                                  lambda data: image(binary,root,data), natural, sharp)
        problems.extend(errors)
        extra = [0 if p['correct'] else 1 for p in presses]
        game_inner = {t: u/1000 for t, u, _, _ in s.carrying}
        for p in presses:
            p['game_inner_ms'] = game_inner.get(p['frame'])
            arrived = s.arrived(p['output_bytes'])
            traced = next((at for t, _, _, at in s.outputs if t == p['frame']), None)
            # An unchanged (even-parity) batch still needs a completed frame trace.
            completed = max(at for at in (arrived,traced) if at is not None) if arrived is not None or traced is not None else None
            p['wall_ms'] = (completed-sent[p['press']-1])*1000 if completed is not None else None
            p['host_stall_ms'] = probe.worst(sent[p['press']-1], completed)*1000 if completed is not None else None
            (root/f"frame-{p['press']:02}.bin").write_bytes(s.out[:p['output_bytes']])
        (root/'trace.err').write_bytes(s.err)
        (root/'complete.bin').write_bytes(s.out)
        final = image(binary,root,measured)
        if final != natural: problems.append('forty recorded toggles did not restore the exact initial frame')
        alive = max([len(p['pids']) for p in polls], default=0)
        if is_mac and (not polls or alive == 0): problems.append('storm never observed a real player')
        if alive > 1: problems.append(f'audition children alive: {alive}, wanted <=1')
        latencies = [p['wall_ms'] for p in presses if p['wall_ms'] is not None]
        if len(latencies)!=40: problems.append(f'only {len(latencies)}/40 presses have an exact correct carrying frame')
        if latencies and min(latencies) < 0: problems.append('a frame preceded its press')
        # This is still write-to-parent-observation latency, not game_inner_us,
        # judged on the presses whose window the stall probe shows the host ran
        # on time. Process polling cannot delay this receiver.
        clean = [p['wall_ms'] for p in presses if p['wall_ms'] is not None and p['host_stall_ms'] == 0]
        p99 = sorted(clean)[math.ceil(len(clean)*.99)-1] if len(clean) >= LATENCY_MIN else None
        if p99 is not None and is_mac and p99 > 70: problems.append(f'storm p99 latency {p99} ms exceeds 70 ms over {len(clean)} presses the host ran on time')
        if b'AudioQueueStart' in s.out or b'Error:' in s.out: problems.append('player error reached terminal during storm')
        sinks = list(root.glob('audition*.wav'))
        if not is_mac and len(sinks)!=1: problems.append(f'Linux audition sink grew to {len(sinks)} files, wanted one rewritten file')
        if not is_mac and (not sinks or sinks[0].read_bytes() != (root/'note-21-0.wav').read_bytes()):
            problems.append('Linux sink did not retain the final natural C3 WAV intact')
        inner_latencies = [p['game_inner_ms'] for p in presses if p['game_inner_ms'] is not None]
        inner_p99 = max(inner_latencies) if len(inner_latencies)==40 else None
        span = presses[-1]['frame'] - presses[0]['frame'] if presses else None
        result = dict(children_alive_max=alive,p99_ms=p99,observer_p99_ms=p99,
                      clean_presses=len(clean),all_presses_max_ms=max(latencies,default=None),
                      game_inner_p99_ms=inner_p99,
                      send_gaps_ms=[(b-a)*1000 for a,b in zip(sent,sent[1:])],
                      row_late_max_ms=max(row_late,default=0)*1000,
                      presses=presses,polls=polls,applied_span_ticks=span,
                      host_stalls=len(probe.stalls),host_stall_max_ms=max((d for _, d in probe.stalls), default=0)*1000,
                      session=n,observed_frames=len(presses),
                      unexpected_cells_max=max(extra,default=0),unexpected_cells=extra,
                      intentional_text_cells=changed(cells(natural)[0],cells(sharp)[0]),
                      sink_files=len(sinks),recorded=len(recorded))
        (root/f'measurements-{n}.json').write_text(json.dumps(result,indent=2)+'\n')
        (root/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
        print(f'audition-storm: children max {alive}, observer p99 {p99} ms over {len(clean)}/40 presses the host ran on time, '
              f'game-inner p99 {inner_p99} ms, extra cells {max(extra,default=0)}, sink files {len(sinks)}, keys {len(recorded)}/40, '
              f'applied over {span} ticks, row late max {result["row_late_max_ms"]:.1f} ms, probe {result["host_stalls"]} stalls '
              f'max {result["host_stall_max_ms"]:.1f} ms (session {n})', flush=True)
        if max(row_late, default=0) > ROW_LATE_S:
            return s, 'row', f'the row wrote a press {max(row_late)*1000:.1f} ms after the trace made it due'
        if is_mac and p99 is None:
            return s, 'latency', f'the host ran {40-len(clean)} of 40 presses late (probe: {result["host_stalls"]} stalls, max {result["host_stall_max_ms"]:.1f} ms)'
        return s, None, None

    latency_tries = 0
    for n in range(1, PACED['REDRIVES'] + 1):
        s, why, detail = attempt(n)
        if why is None: break
        if why == 'latency':
            latency_tries += 1
            if latency_tries >= PACED['LATENCY_SESSIONS']:
                print(f'SKIP audition-storm latency: the host stalled more than half the presses in each of {latency_tries} '
                      f'sessions ({detail}); the 70 ms bar was not measured; every press was judged for its state', flush=True)
                break
        print(f'audition-storm: session {n} out of its case ({detail}); driven again', flush=True)
    else:
        problems.append(f'audition-storm: SCHEDULE: the storm was never delivered in {PACED["REDRIVES"]} sessions ({detail})')
    return s, problems


def quiet_sink(binary, ctx):
    # mac-only rows are loud, but still exercise a valid terminal lifecycle.
    s, _ = setup(binary,ctx,'quiet-sink',mute=True)
    s.type(b'q'); s.finish(); problems=[]; ctx.common_checks(s,0,problems)
    return s,problems


def hear_replaces_audition(binary, ctx):
    problems = []

    def attempt(n):
        s, root = setup(binary,ctx,'audition-hear-owner')
        s.type(b' ', 0)
        # Space's acknowledgement is the owned audition it starts.
        began = time.monotonic()
        previous = []
        while not previous and time.monotonic() < began + PACED['LIVENESS_S']:
            previous = children(s)
            s.pump(.002)
        if len(previous)!=1: problems.append(f'Space did not start exactly one owned audition: {previous}')
        probe = PACED['StallProbe'](root)
        sent = time.monotonic(); os.write(s.master,b'h')
        retired_at = polled_ms = None; rendered_first = False
        # h must stop the audition (a liveness bound) before it renders the
        # whole piece: an order no host speed changes (no whole-*.wav may exist
        # while the audition is alive; the WAV is checked before the process
        # table, so a hit means the audition outlived the render). And within
        # 100 ms when the host runs on time, measured exactly as trunk's row
        # measured it: a pgrep -P begun within 100 ms of h finds it gone.
        while time.monotonic()-sent < PACED['LIVENESS_S']:
            s.pump(.002)
            began = time.monotonic()
            wav = any(root.glob('whole-*.wav'))
            if not set(previous).intersection(children(s)):
                retired_at = time.monotonic(); polled_ms = (began-sent)*1000; break
            if wav: rendered_first = True
        probe.stop()
        stopped_ms = ((retired_at or time.monotonic())-sent)*1000
        stall_ms = probe.worst(sent, sent + max(stopped_ms, 100)/1000)*1000
        if retired_at is None: problems.append('h did not kill and reap the audition')
        elif polled_ms > 100 and stall_ms == 0: problems.append(f'h did not kill and reap the audition within 100 ms (seen gone by a poll begun at {polled_ms:.3f} ms, the host on time)')
        if rendered_first: problems.append('h rendered the whole piece before it stopped the audition')
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
        print(f'audition-hear-owner: retired {previous} in {stopped_ms:.3f} ms (the poll that saw it gone began at '
              f'{polled_ms if polled_ms is None else round(polled_ms, 3)} ms); whole {whole}; '
              f'host stall in the window {stall_ms:.1f} ms (session {n})', flush=True)
        (root/'measurements.json').write_text(json.dumps(dict(audition=previous,retired=retired_at is not None,stop_ms=stopped_ms,polled_ms=polled_ms,
                                                              rendered_first=rendered_first,
                                                              host_stall_ms=stall_ms,whole=whole,session=n),indent=2)+'\n')
        return s, retired_at is not None and polled_ms > 100 and stall_ms > 0, stall_ms

    for n in range(1, PACED['LATENCY_SESSIONS'] + 1):
        s, unmeasured, stall_ms = attempt(n)
        if not unmeasured: break
        print(f'audition-hear-owner: session {n} could not measure the retire (the host ran a wake {stall_ms:.1f} ms late in the window)'
              + ('; driven again' if n < PACED['LATENCY_SESSIONS'] else ''), flush=True)
    else:
        print(f'SKIP audition-hear-owner latency: the host stalled the retire window in each of {PACED["LATENCY_SESSIONS"]} '
              f'sessions (probe max {stall_ms:.1f} ms); the 100 ms bar was not measured; the retire itself was judged', flush=True)
    return s,problems


# The common gate loads only rows applicable to its actual host: two Mac
# regressions plus a whole-player ownership check, or the Linux sink parity.
ROWS = ({'quiet-player-stderr':quiet_failure, 'audition-storm':storm,
         'audition-hear-owner':hear_replaces_audition} if Path('/usr/bin/afplay').exists()
        else {'linux-audition-sink':storm})
