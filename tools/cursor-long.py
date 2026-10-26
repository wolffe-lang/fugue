#!/usr/bin/env python3
"""Long, bounded whole-page pty traversal, with per-press p99/max latency.

Four full out-and-back walks (632 presses at 30 Hz) cross every held value,
barline and scrolling boundary. Geometry expectations are independent fixture
arithmetic, not an import or headless render of the game's layout function.
"""
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import time


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)] if values else None


def check(binary, ctx):
    root = Path(ctx.ROOT)/'target/pty/cursor-long'
    root.mkdir(parents=True, exist_ok=True)
    Frames = runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-check.py'))['frame_session'](ctx)
    lengths = [4,4,4,4,2,2,2,2,8,4,4,4,4,2,2,2,2,8,4,4,8]
    onsets = []; elapsed = 0
    for value in lengths: onsets.append(elapsed); elapsed += value
    assert elapsed == 80
    # Current unedited Book V tutorial: pitch and interval labels fit these
    # value minima. Every editable eighth additionally needs its own caret cell.
    widths = [max(value, 6 if value >= 8 else 5 if value >= 4 else 4) for value in lengths]

    def column(position, cols):
        event = max(i for i, onset in enumerate(onsets) if onset <= position)
        def x_at(first):
            return 9 + sum(widths[i] + ((onsets[i]+lengths[i])%8 == 0)
                           for i in range(event) if onsets[i] >= first*8)
        first = 0
        while first < position//8 and x_at(first)+widths[event]-2 >= cols-27: first += 1
        return x_at(first) + position-onsets[event]

    problems, journal, last = [], [], None
    for cols, rows in [(80,24),(120,40)]:
        for tier in ['rich','plain']:
            for mute in [False,True]:
                name = f'{cols}x{rows}-{tier}-' + ('mute' if mute else 'sound')
                case = root/name; case.mkdir(parents=True, exist_ok=True)
                env = ctx.env_for(); env['FUGUE_SOUND'] = '1'; env['FUGUE_AUDIO_TRACE'] = '1'
                env['TMPDIR'] = os.environ.get('TMPDIR', str(root))
                env['FUGUE_STATE'] = str(case/'state')
                s = Frames([binary,'--book','5','--no-title','--trace','--size',f'{cols}x{rows}',
                            '--tier',tier,'--record',str(case/'record.pk')] + (['--mute'] if mute else []), rows, cols, env)
                last = s
                deadline = time.monotonic()+30
                while not s.out and time.monotonic() < deadline: s.pump(.02)
                s.pump(.1)
                initial_bytes = s.out
                sent = []; start = time.monotonic()
                sequence = (['right']*79 + ['left']*79)*4
                for index, key in enumerate(sequence):
                    sent.append(time.monotonic())
                    os.write(s.master, b'\x1b[C' if key == 'right' else b'\x1b[D')
                    s.pump(max(.001, start+(index+1)/30-time.monotonic()))
                s.pump(.2); s.type(b'q'); s.finish()
                ctx.common_checks(s, 0, problems)
                (case/'capture.bin').write_bytes(s.out); (case/'trace.err').write_bytes(s.err)
                events = [(int(line.split()[1]),line.split()[2]) for line in (case/'record.pk').read_text().splitlines()
                          if line.startswith('t ') and line.split()[2] in ['right','left']]
                if [key for _,key in events] != sequence: problems.append(name+': lost/reordered long-run keys')
                if s.err.count(b'note-bank render_us') != (0 if mute else 1):
                    problems.append(name+': navigation re-prepared the audio bank')
                # Group the actual recording by carrying frame. Late clock catch-up
                # is kept as >1 frame, never silently rounded down to one.
                by_frame = {}
                for index,(at,key) in enumerate(events):
                    carrying = next((tick for tick,_ in s.frames if tick > at), None)
                    if carrying is None: problems.append(name+': no carrying frame'); continue
                    by_frame.setdefault(carrying,[]).append((index,at,key))
                initial_path = case/'initial.bin'; initial_path.write_bytes(initial_bytes)
                applied = subprocess.run([binary,'--apply',str(initial_path),'--size',f'{cols}x{rows}'],
                                         capture_output=True, check=True)
                initial_image = applied.stdout.decode().split('--\n')[0].splitlines()
                initial_caret = [(y,x) for y,line in enumerate(initial_image) for x,ch in enumerate(line[:cols-24]) if ch=='^']
                position = 0; presses = []; previous = initial_caret
                for tick,data in s.frames:
                    keys = by_frame.get(tick,[])
                    if not keys: continue
                    for _,_,key in keys: position += 1 if key == 'right' else -1
                    cap = case/'frame.bin'; cap.write_bytes(data)
                    applied = subprocess.run([binary,'--apply',str(cap),'--size',f'{cols}x{rows}'],
                                             capture_output=True, check=True)
                    image = applied.stdout.decode().split('--\n')[0].splitlines()
                    caret = [(y,x) for y,line in enumerate(image) for x,ch in enumerate(line[:cols-24]) if ch=='^']
                    panel = f'Bar {position//8+1}, beat {position%8+1}:8' in image[5][cols-22:]
                    aligned = len(caret)==1 and caret[0][1]==column(position,cols)
                    for index,at,key in keys:
                        presses.append({'press':index+1,'key':key,'record_tick':at,'frame':tick,
                                        'frames':tick-at,'wall_ms':(s.frame_times[tick]-sent[index])*1000,
                                        'position':position,'panel':panel,'aligned':aligned,'caret':caret,
                                        'changed':previous is None or previous!=caret,'coalesced':len(keys)})
                    previous = caret
                for i,p in enumerate(presses):
                    prior = initial_caret if i == 0 else presses[i-1]['caret']
                    future = next((q for q in presses[i:] if q['caret']!=prior),None)
                    p['next_visible_change_frames'] = None if future is None else future['frame']-p['record_tick']
                frames = [p['frames'] for p in presses]; wall = [p['wall_ms'] for p in presses]
                updates = [p['next_visible_change_frames'] for p in presses if p['next_visible_change_frames'] is not None]
                wrong = [p for p in presses if not p['panel'] or not p['aligned'] or p['frames']>1]
                if len(presses)!=632 or wrong:
                    problems.append(f'{name}: {len(presses)}/632 captured; {len(wrong)} stale/late presses; '
                                    f'frame p99/max {percentile(frames,.99)}/{max(frames,default=0)}')
                summary = {'case':name,'count':len(presses),'recorded':len(events),'wrong':len(wrong),
                           'repeat_hz':30,'frame_p99':percentile(frames,.99),'frame_max':max(frames,default=0),
                           'wall_p99_ms':percentile(wall,.99),'wall_max_ms':max(wall,default=0),
                           'next_visible_change_p99_frames':percentile(updates,.99),
                           'next_visible_change_max_frames':max(updates,default=0),
                           'never_changed_before_quit':sum(p['next_visible_change_frames'] is None for p in presses),
                           'final_position':position,'presses':presses}
                journal.append(summary)
                (root/'measurements.json').write_text(json.dumps(journal,indent=2)+'\n')
                print(f'cursor-long: {name}: {len(presses)} presses, stale/late {len(wrong)}; '
                      f'frame p99/max {summary["frame_p99"]}/{summary["frame_max"]}; '
                      f'wall p99/max {summary["wall_p99_ms"]:.3f}/{summary["wall_max_ms"]:.3f} ms; '
                      f'next visible change p99/max {summary["next_visible_change_p99_frames"]}/'
                      f'{summary["next_visible_change_max_frames"]}; end {position}', flush=True)
    return last, problems
