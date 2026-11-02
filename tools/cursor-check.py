#!/usr/bin/env python3
"""Actual pty presses, the game's own trace, terminal cells and replay key accounting.

Loaded by the engine's cursor-same-frame row. No synthetic input/state/frame seam.
Every press goes through tests/paced.py (fg04, fugue#36): written by the game's
trace (a 30 Hz burst is one press a tick), acknowledged by its carrying frame,
and judged at that frame's exact output boundary. After the session each
recorded key is placed in the first carrying frame after its record tick, so a
frame that carries two presses (a late wake) is judged with both.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess


def paced(ctx):
    return runpy.run_path(str(Path(ctx.ROOT) / 'tests/paced.py'))


def book_five_attack(event, cols):
    """Independent arithmetic for the shipped Book V tutorial engraving."""
    lengths = [4,4,4,4,2,2,2,2,8,4,4,4,4,2,2,2,2,8,4,4,8]
    onsets = [sum(lengths[:i]) for i in range(len(lengths))]
    widths = [max(n, 6 if n >= 8 else 5 if n >= 4 else 4) for n in lengths]
    def x_at(first):
        return 9 + sum(widths[i] + ((onsets[i]+lengths[i])%8 == 0)
                       for i in range(event) if onsets[i] >= first*8)
    first = 0
    while first < onsets[event]//8 and x_at(first)+widths[event]-2 >= cols-27:
        first += 1
    return onsets[event], x_at(first)


def check(binary, ctx):
    root = Path(ctx.ROOT) / 'target/pty/cursor-same-frame'
    root.mkdir(parents=True, exist_ok=True)
    problems, measurements = [], []
    last = None
    P = paced(ctx)
    Session = P['session'](ctx)

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
                s = Session([binary, '--book', '5', '--no-title', '--size', f'{cols}x{rows}',
                             '--tier', tier, '--trace', '--record', str(path)] + (['--mute'] if mute else []), rows, cols, env)
                last = s
                s.ready()
                initial = s.frame()
                # Right/Left singly, then ten Rights and ten Lefts, one a tick
                # (30 Hz) by the game's trace.
                for key in [b'\x1b[C', b'\x1b[D']:
                    s.send(key)
                for key in [b'\x1b[C', b'\x1b[D']:
                    s.burst(key, 10)
                s.type(b'q'); s.finish()
                ctx.common_checks(s, 0, problems)
                (root / (name + '.bin')).write_bytes(s.out)
                (root / (name + '.err')).write_bytes(s.err)
                keys = s.verify(path, name, problems)
                events = [(t, k) for t, k in keys if k in ('left', 'right')]
                if [k for _, k in events] != ['right', 'left'] + ['right']*10 + ['left']*10:
                    problems.append(name + ': lost or reordered presses')
                press_of = {}
                for i, (t, k) in enumerate(keys):
                    if k in ('left', 'right'):
                        press_of[i] = len(press_of)
                # Apply the actual output bytes with the game's terminal model.
                def image(data):
                    capture = root / 'frame.bin'; capture.write_bytes(data)
                    applied = subprocess.run([binary, '--apply', str(capture), '--size', f'{cols}x{rows}'],
                                             capture_output=True, check=True)
                    return applied.stdout.decode().split('--\n')[0].splitlines()
                def caret(screen):
                    return [(y, x) for y, line in enumerate(screen) for x, ch in enumerate(line[:cols-24]) if ch == '^']
                previous = caret(image(initial))
                time_position = 0
                per_press = []
                by_frame = P['carrying_frames'](keys, [c[0] for c in s.carrying])
                for tick in sorted(by_frame):
                    carried = [(press_of[i], t, k) for i, t, k in by_frame[tick] if i in press_of]
                    if not carried: continue
                    for _, _, key in carried: time_position += 1 if key == 'right' else -1
                    data = s.frame(tick)
                    screen = image(data)
                    onset, expected_x = book_five_attack(time_position, cols)
                    panel = f'Bar {onset//8+1}, beat {onset%8+1}:8' in screen[5][cols-22:]
                    current = caret(screen)
                    moved = bool(current) and current != previous
                    # Positions are events, never subdivisions of held values.
                    aligned = len(current) == 1 and current[0][1] == expected_x
                    frame_dir = root / name
                    frame_dir.mkdir(exist_ok=True)
                    (frame_dir / f'frame-{tick}.bin').write_bytes(data)
                    for index, at, key in carried:
                        per_press.append({'press': index+1, 'key': key, 'record_tick': at, 'frame': tick,
                                          'panel_frames': 1 if panel else None,
                                          'cursor_frames': 1 if moved else None,
                                          'caret': current, 'expected_x': expected_x,
                                          'aligned': aligned, 'coalesced': len(carried)})
                    if not panel or not aligned:
                        problems.append(f'{name}: press {carried[0][0]+1} frame {tick}: panel={panel}, caret moved={moved}, aligned={aligned}, {previous}->{current}')
                    previous = current
                if len(per_press) != 22: problems.append(f'{name}: only {len(per_press)}/22 presses have a captured frame')
                late = s.lateness()
                result = {'case': name, 'repeat_hz': 30, 'paced': 'trace', 'presses': per_press,
                          'recorded': len(events), 'final_time': time_position,
                          'late_ticks': late, 'acks': s.acks}
                measurements.append(result)
                (root / 'measurements.json').write_text(json.dumps(measurements, indent=2)+'\n')
                print(f'cursor-same-frame: {name}: {len(per_press)} presses, '
                      f'panel {sum(p["panel_frames"] == 1 for p in per_press)}/22 same-frame, '
                      f'caret {sum(p["cursor_frames"] == 1 for p in per_press)}/22 same-frame; '
                      f'end {time_position}; 30 Hz by the trace, late ticks max {max(late, default=0)}')
    return last, problems
