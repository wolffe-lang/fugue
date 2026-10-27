#!/usr/bin/env python3
"""Real input: one attack per Left/Right, exactly one caret, all six books."""
import json
import os
from pathlib import Path
import runpy
import subprocess


def check(binary, ctx):
    root = Path(ctx.ROOT)/'target/pty/event-caret'
    root.mkdir(parents=True, exist_ok=True)
    output = subprocess.run([binary, '--event-map'], capture_output=True, text=True, check=True).stdout
    maps = {}
    for line in output.splitlines():
        tag, book, cols, event, onset, column = line.split()
        assert tag == 'event-map'
        maps.setdefault((int(book), int(cols)), []).append((int(event), int(onset), int(column)))
    Frames = runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-check.py'))['frame_session'](ctx)
    problems, journal, last = [], [], None
    for book in range(1, 7):
        for cols, rows in [(80, 24), (120, 40)]:
            for tier in ['rich', 'plain']:
                name = f'book-{book}-{cols}-{tier}'
                case = root/name
                case.mkdir(exist_ok=True)
                env = ctx.env_for()
                env['TMPDIR'] = os.environ.get('TMPDIR', str(root))
                env['FUGUE_STATE'] = str(case/'state')
                record = case/'record.pk'
                s = Frames([binary, '--book', str(book), '--size', f'{cols}x{rows}', '--no-title',
                            '--tier', tier, '--trace', '--record', str(record)], rows, cols, env)
                last = s
                s.pump(.2)
                captures = [(0, s.out)]
                sequence = ['right']*8 + ['left']*8
                for key in sequence:
                    s.type(b'\x1b[C' if key == 'right' else b'\x1b[D', .08)
                # A single-note audition must not move the navigation caret.
                s.type(b' ', .12)
                s.type(b'q'); s.finish()
                ctx.common_checks(s, 0, problems)
                events = [(int(line.split()[1]), line.split()[2]) for line in record.read_text().splitlines()
                          if line.startswith('t ') and line.split()[2] in ['left', 'right', 'sound']]
                if [key for _, key in events] != sequence + ['sound']:
                    problems.append(name + ': lost/reordered input')
                index = 0
                checked = 0
                for tick, data in s.frames:
                    keys = [key for at, key in events if at == tick-1]
                    if not keys: continue
                    for key in keys:
                        if key == 'right': index += 1
                        if key == 'left': index -= 1
                    path = case/f'frame-{tick}.bin'
                    path.write_bytes(data)
                    screen = subprocess.run([binary,'--apply',str(path),'--size',f'{cols}x{rows}'],
                                            capture_output=True, check=True).stdout.decode().split('--\n')[0].splitlines()
                    carets = [(y,x) for y,line in enumerate(screen) for x,ch in enumerate(line) if ch == '^']
                    _, onset, x = maps[(book,cols)][index]
                    status = f'Bar {onset//8+1}, beat {onset%8+1}:8'
                    aligned = len(carets) == 1 and carets[0][1] == x
                    row = dict(case=name,frame=tick,keys=keys,event=index,onset=onset,expected_column=x,carets=carets,
                               aligned=aligned,status=status in screen[5])
                    journal.append(row)
                    if not aligned or not row['status']:
                        problems.append(f'{name}: event-caret frame {tick} selected {index}: {row}')
                    checked += len(keys)
                if checked != 17: problems.append(f'{name}: {checked}/17 carrying-frame keys')
                (case/'capture.bin').write_bytes(s.out)
                (case/'trace.err').write_bytes(s.err)
                print(f'event-caret: {name}: {checked}/17 presses; event/attack/status and stationary audition checked', flush=True)
    (root/'measurements.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last, problems
