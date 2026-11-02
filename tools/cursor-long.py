#!/usr/bin/env python3
"""Long, bounded whole-page pty traversal, with per-press p99/max latency.

Four full out-and-back walks (160 presses at 30 Hz) cross every notated event,
barline and scrolling boundary. p99 must be <=70 ms and worst press <=100 ms,
so an isolated blocking handoff cannot hide behind a fast median.
Geometry expectations are independent fixture
arithmetic, not an import or headless render of the game's layout function.

Every press goes through tests/paced.py (fg04, fugue#36): one a tick by the
game's trace, acknowledged by its carrying frame, judged at that frame's exact
output boundary. Every press's panel and caret are judged in every session.
The latency claims (drawn by the first wake after the press, the 70/100 ms
bars) are judged on every press whose window the stall probe shows the host
ran on time, and never forgiven there; a session in which the host stalled
more than half the presses cannot measure the game's latency and is driven
again once; a latency no session could measure is a loud, counted SKIP.
"""
import json
import math
import os
from pathlib import Path
import runpy
import subprocess


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)] if values else None


def check(binary, ctx):
    root = Path(ctx.ROOT)/'target/pty/cursor-long'
    root.mkdir(parents=True, exist_ok=True)
    P = runpy.run_path(str(Path(ctx.ROOT)/'tests/paced.py'))
    Session = P['session'](ctx)
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
        return x_at(first)

    problems, journal, last = [], [], None

    def walk(name, cols, rows, tier, mute, attempt):
        case = root/name; case.mkdir(parents=True, exist_ok=True)
        env = ctx.env_for(); env['FUGUE_SOUND'] = '1'; env['FUGUE_AUDIO_TRACE'] = '1'
        env['TMPDIR'] = os.environ.get('TMPDIR', str(root))
        env['FUGUE_STATE'] = str(case/'state')
        s = Session([binary,'--book','5','--no-title','--trace','--size',f'{cols}x{rows}',
                     '--tier',tier,'--record',str(case/'record.pk')] + (['--mute'] if mute else []), rows, cols, env)
        s.ready()
        initial_bytes = s.frame()
        probe = P['StallProbe'](case)
        sequence = (['right']*20 + ['left']*20)*4
        start = s.tick + 1
        try:
            acks = [s.send(b'\x1b[C' if key == 'right' else b'\x1b[D', at=start+index)
                    for index, key in enumerate(sequence)]
        finally:
            probe.stop()
        s.type(b'q'); s.finish()
        ctx.common_checks(s, 0, problems)
        (case/'capture.bin').write_bytes(s.out); (case/'trace.err').write_bytes(s.err)
        recorded = s.verify(case/'record.pk', name, problems)
        events = [(t, k) for t, k in recorded if k in ['right','left']]
        if [key for _,key in events] != sequence: problems.append(name+': lost/reordered long-run keys')
        if s.err.count(b'note-bank render_us') != (0 if mute else 1):
            problems.append(name+': navigation re-prepared the audio bank')
        # Group the actual recording by carrying frame. Late clock catch-up
        # is kept as >1 frame, never silently rounded down to one.
        press_of = {}
        for i, (t, k) in enumerate(recorded):
            if k in ('right', 'left'): press_of[i] = len(press_of)
        by_frame = P['carrying_frames'](recorded, [c[0] for c in s.carrying])
        seen = {t: at for t, _, _, at in s.carrying}
        initial_path = case/'initial.bin'; initial_path.write_bytes(initial_bytes)
        applied = subprocess.run([binary,'--apply',str(initial_path),'--size',f'{cols}x{rows}'],
                                 capture_output=True, check=True)
        initial_image = applied.stdout.decode().split('--\n')[0].splitlines()
        initial_caret = [(y,x) for y,line in enumerate(initial_image) for x,ch in enumerate(line[:cols-24]) if ch=='^']
        position = 0; presses = []; previous = initial_caret
        for tick in sorted(by_frame):
            keys = [(press_of[i], at, key) for i, at, key in by_frame[tick] if i in press_of]
            if not keys: continue
            for _,_,key in keys: position += 1 if key == 'right' else -1
            cap = case/'frame.bin'; cap.write_bytes(s.frame(tick))
            applied = subprocess.run([binary,'--apply',str(cap),'--size',f'{cols}x{rows}'],
                                     capture_output=True, check=True)
            image = applied.stdout.decode().split('--\n')[0].splitlines()
            caret = [(y,x) for y,line in enumerate(image) for x,ch in enumerate(line[:cols-24]) if ch=='^']
            onset = onsets[position]
            panel = f'Bar {onset//8+1}, beat {onset%8+1}:8' in image[5][cols-22:]
            aligned = len(caret)==1 and caret[0][1]==column(onset,cols)
            for index,at,key in keys:
                sent = acks[index]['written']
                presses.append({'press':index+1,'key':key,'record_tick':at,'frame':tick,
                                'frames':tick-at,'wall_ms':(seen[tick]-sent)*1000,
                                'host_stall_ms':probe.worst(sent, seen[tick])*1000,
                                'target':acks[index]['target'],
                                'position':position,'panel':panel,'aligned':aligned,'caret':caret,
                                'changed':previous is None or previous!=caret,'coalesced':len(keys)})
            previous = caret
        for i,p in enumerate(presses):
            prior = initial_caret if i == 0 else presses[i-1]['caret']
            future = next((q for q in presses[i:] if q['caret']!=prior),None)
            p['next_visible_change_frames'] = None if future is None else future['frame']-p['record_tick']
        # Correctness: every press, every session.
        wrong = [p for p in presses if not p['panel'] or not p['aligned']]
        # Latency: the presses the host ran on time.
        clean = [p for p in presses if p['host_stall_ms'] == 0]
        late = [p for p in clean if p['frames'] > 1]
        frames = [p['frames'] for p in clean]; wall = [p['wall_ms'] for p in clean]
        if len(presses)!=160 or wrong or late:
            problems.append(f'{name}: {len(presses)}/160 captured; {len(wrong)} stale presses, {len(late)} late of {len(clean)} the host ran on time; '
                            f'frame p99/max {percentile(frames,.99)}/{max(frames,default=0)}')
        measured = len(clean) * 2 >= len(presses) and len(presses) == 160
        if measured and wall and (percentile(wall,.99) > 70 or max(wall) > 100):
            problems.append(f'{name}: periodic wall stall: p99={percentile(wall,.99):.3f} ms, max={max(wall):.3f} ms (bars 70/100) over {len(clean)} presses the host ran on time')
        updates = [p['next_visible_change_frames'] for p in presses if p['next_visible_change_frames'] is not None]
        everything = [p['wall_ms'] for p in presses]
        summary = {'case':name,'session':attempt,'count':len(presses),'recorded':len(events),'wrong':len(wrong),
                   'clean':len(clean),'late':len(late),'latency_measured':measured,
                   'repeat_hz':30,'paced':'trace','frame_p99':percentile(frames,.99),'frame_max':max(frames,default=0),
                   'wall_p99_ms':percentile(wall,.99),'wall_max_ms':max(wall,default=0),
                   'all_presses_wall_p99_ms':percentile(everything,.99),'all_presses_wall_max_ms':max(everything,default=0),
                   'next_visible_change_p99_frames':percentile(updates,.99),
                   'next_visible_change_max_frames':max(updates,default=0),
                   'never_changed_before_quit':sum(p['next_visible_change_frames'] is None for p in presses),
                   'host_stalls':len(probe.stalls),'host_stall_max_ms':max((d for _, d in probe.stalls), default=0)*1000,
                   'late_ticks':s.lateness(),
                   'final_position':position,'presses':presses}
        journal.append(summary)
        (root/'measurements.json').write_text(json.dumps(journal,indent=2)+'\n')
        print(f'cursor-long: {name}: {len(presses)} presses, stale {len(wrong)}, late {len(late)}; '
              f'host on time for {len(clean)}/{len(presses)} (probe: {summary["host_stalls"]} stalls, max {summary["host_stall_max_ms"]:.1f} ms); '
              + (f'frame p99/max {summary["frame_p99"]}/{summary["frame_max"]}; '
                 f'wall p99/max {summary["wall_p99_ms"]:.3f}/{summary["wall_max_ms"]:.3f} ms over those; '
                 if wall else '')
              + f'next visible change p99/max {summary["next_visible_change_p99_frames"]}/'
              f'{summary["next_visible_change_max_frames"]}; end {position} (session {attempt})', flush=True)
        return s, summary

    skipped = 0
    for cols, rows in [(80,24),(120,40)]:
        for tier in ['rich','plain']:
            for mute in [False,True]:
                name = f'{cols}x{rows}-{tier}-' + ('mute' if mute else 'sound')
                for attempt in range(1, P['LATENCY_SESSIONS'] + 1):
                    last, summary = walk(name, cols, rows, tier, mute, attempt)
                    if summary['latency_measured']:
                        break
                    print(f'cursor-long: {name}: session {attempt} could not measure latency (the host ran {summary["count"]-summary["clean"]} '
                          f'of {summary["count"]} presses late; the probe saw {summary["host_stalls"]} stalls, max '
                          f'{summary["host_stall_max_ms"]:.1f} ms)' + ('; driven again' if attempt < P['LATENCY_SESSIONS'] else ''), flush=True)
                else:
                    skipped += 1
                    print(f'SKIP cursor-long {name} latency: the host stalled more than half the presses in each of '
                          f'{P["LATENCY_SESSIONS"]} sessions (probe max {summary["host_stall_max_ms"]:.1f} ms); the bars were not '
                          f'measured; every press was judged for its frame', flush=True)
    if skipped:
        print(f'cursor-long: SKIP count {skipped} of 8 cases (latency on a stalled host)', flush=True)
    return last, problems
