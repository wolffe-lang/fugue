#!/usr/bin/env python3
"""Actual pty presses, frame-tick traces, terminal cells and replay key accounting.

Loaded by the engine's cursor-same-frame row. No synthetic input/state/frame seam.
The capture includes one frame snapshot for every key-carrying trace; unchanged
idle frames need no bytes. 30 Hz repeat is paced on monotonic deadlines.
"""
import json
import os
from pathlib import Path
import re
import select
import time


def check(binary, ctx):
    root = Path(ctx.ROOT) / 'target/pty/cursor-same-frame'
    root.mkdir(parents=True, exist_ok=True)
    problems, measurements = [], []
    last = None

    class Frames(ctx.Session):
        def __init__(self, *args):
            self.frames, self.trace_count = [], 0
            super().__init__(*args)

        def pump(self, seconds):
            end = time.monotonic() + seconds
            while time.monotonic() < end:
                fds = [self.r_err] + ([] if self.eof else [self.master])
                ready, _, _ = select.select(fds, [], [], min(.002, max(0, end-time.monotonic())))
                # The write to the pty precedes the trace on the stderr pipe.
                if self.master in ready:
                    try: chunk = os.read(self.master, 65536)
                    except OSError: chunk = b''
                    if chunk: self.out += chunk
                    else: self.eof = True
                if self.r_err in ready:
                    chunk = os.read(self.r_err, 65536)
                    if chunk: self.err += chunk
                traces = re.findall(rb'trace frame (\d+) carries_key', self.err)
                if len(traces) > self.trace_count:
                    while not self.eof and select.select([self.master], [], [], 0)[0]:
                        try: chunk = os.read(self.master, 65536)
                        except OSError: chunk = b''
                        if not chunk: self.eof = True; break
                        self.out += chunk
                    for tick in traces[self.trace_count:]:
                        self.frames.append((int(tick), self.out))
                    self.trace_count = len(traces)

    for cols, rows in [(80, 24), (120, 40)]:
        for tier in ['rich', 'plain']:
            for mute in [False, True]:
                name = f'{cols}x{rows}-{tier}-' + ('mute' if mute else 'sound')
                path = root / (name + '.pk')
                env = ctx.env_for()
                env['TMPDIR'] = os.environ.get('TMPDIR', str(root))
                env['FUGUE_STATE'] = str(root / (name + '.state'))
                env['FUGUE_AUDIO_TRACE'] = '1'
                env['FUGUE_SOUND'] = '1'
                s = Frames([binary, '--book', '5', '--no-title', '--size', f'{cols}x{rows}',
                            '--tier', tier, '--trace', '--record', str(path)] + (['--mute'] if mute else []), rows, cols, env)
                last = s
                deadline = time.monotonic() + 30
                while not s.out and time.monotonic() < deadline: s.pump(.02)
                s.pump(.1)
                initial = s.out
                # Right/Left singly, then ten Rights and ten Lefts at 30 Hz.
                for key in [b'\x1b[C', b'\x1b[D']:
                    s.type(key, .20)
                for key in [b'\x1b[C', b'\x1b[D']:
                    start = time.monotonic()
                    for press in range(10):
                        os.write(s.master, key)
                        s.pump(max(.001, start + (press+1)/30 - time.monotonic()))
                    s.pump(.2)
                s.type(b'q'); s.finish()
                ctx.common_checks(s, 0, problems)
                (root / (name + '.bin')).write_bytes(s.out)
                (root / (name + '.err')).write_bytes(s.err)
                events = [(int(line.split()[1]), line.split()[2]) for line in path.read_text().splitlines()
                          if line.startswith('t ') and line.split()[2] in ['left', 'right']]
                if [key for _, key in events] != ['right', 'left'] + ['right']*10 + ['left']*10:
                    problems.append(name + ': lost or reordered presses')
                # Apply the actual output bytes with the game's terminal model.
                # Each trace is the frame that carries all keys recorded at tick-1.
                def image(data):
                    capture = root / 'frame.bin'; capture.write_bytes(data)
                    import subprocess
                    applied = subprocess.run([binary, '--apply', str(capture), '--size', f'{cols}x{rows}'],
                                             capture_output=True, check=True)
                    return applied.stdout.decode().split('--\n')[0].splitlines()
                def caret(screen):
                    return [(y, x) for y, line in enumerate(screen) for x, ch in enumerate(line[:cols-24]) if ch == '^']
                previous = caret(image(initial))
                time_position = 0
                per_press = []
                for tick, data in s.frames:
                    keys = [(index, key) for index, (at, key) in enumerate(events) if at == tick-1]
                    if not keys: continue
                    for _, key in keys: time_position += 1 if key == 'right' else -1
                    screen = image(data)
                    panel = f'Bar {time_position//8+1}, beat {time_position%8+1}:8' in screen[5][cols-22:]
                    current = caret(screen)
                    moved = bool(current) and current != previous
                    # The first two bars are four halves, five cells each,
                    # separated by one bar gutter. Eighth offsets occupy cells.
                    expected_x = 9 + time_position//8*11 + time_position%8//4*5 + time_position%4
                    aligned = len(current) == 1 and current[0][1] == expected_x
                    frame_dir = root / name
                    frame_dir.mkdir(exist_ok=True)
                    (frame_dir / f'frame-{tick}.bin').write_bytes(data)
                    for index, key in keys:
                        per_press.append({'press': index+1, 'key': key, 'frame': tick,
                                          'panel_frames': 1 if panel else None,
                                          'cursor_frames': 1 if moved else None,
                                          'caret': current, 'expected_x': expected_x,
                                          'aligned': aligned, 'coalesced': len(keys)})
                    if not panel or not moved or not aligned:
                        problems.append(f'{name}: press {keys[0][0]+1} frame {tick}: panel={panel}, caret moved={moved}, aligned={aligned}, {previous}->{current}')
                    previous = current
                if len(per_press) != 22: problems.append(f'{name}: only {len(per_press)}/22 presses have a captured frame')
                result = {'case': name, 'repeat_hz': 30, 'presses': per_press,
                          'recorded': len(events), 'final_time': time_position}
                measurements.append(result)
                (root / 'measurements.json').write_text(json.dumps(measurements, indent=2)+'\n')
                print(f'cursor-same-frame: {name}: {len(per_press)} presses, '
                      f'panel {sum(p["panel_frames"] == 1 for p in per_press)}/22 same-frame, '
                      f'caret {sum(p["cursor_frames"] == 1 for p in per_press)}/22 same-frame; '
                      f'end {time_position}; 30 Hz')
    return last, problems
