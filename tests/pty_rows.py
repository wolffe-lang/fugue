"""Editor witnesses use actual terminal bytes and inspect the engine's WAV output.

Every key is typed through tests/paced.py (fg04, fugue#36): written once the
game has drawn, acknowledged by the game's own trace, and every screen is read
at the acknowledging frame's exact output boundary. No row decides anything
by a sleep; the only wall-clock bounds left are liveness bounds on observables
(a file, a stderr line, a child process) and the latency bars the rows state.
"""
from pathlib import Path
import runpy
import struct
import time
import shutil
import subprocess

PACED = runpy.run_path(str(Path(__file__).with_name('paced.py')))


def paced(ctx, argv, rows, cols, env, base=None):
    """A trace-keyed session (--trace added), its first frame awaited."""
    s = PACED['session'](ctx, base)(list(argv) + ['--trace'], rows, cols, env)
    s.ready()
    return s


def untraced(err):
    """stderr as the row printed it before --trace: the trace lines left out."""
    return b''.join(line for line in err.splitlines(True) if not line.startswith(b'trace ')).decode(errors='replace')


def screen(bin, ctx, s, ack):
    """The 80x24 screen at an acknowledged frame's exact boundary."""
    return ctx.screen_text(bin, s.frame(ack['frame']))


def editor(bin, ctx):
    root = Path(ctx.ROOT) / 'target/pty/audio'
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    env = ctx.env_for()
    env['FUGUE_WAV_DIR'] = str(root)
    env['FUGUE_AUDIO_TRACE'] = '1'
    s = paced(ctx, [bin, '--seed', '7', '--no-title'], 24, 80, env)
    problems = []
    # The bank is prepared before the terminal opens, so before the first frame.
    if b'note-bank render_us' not in s.err:
        problems.append('note bank did not prepare')
    s.send(b'\x1b[A')
    s.send(b'\x1b[B')
    s.send(b'h')
    deadline = time.monotonic() + 15
    while not list(root.glob('whole-*.wav')) and time.monotonic() < deadline:
        s.pump(.1)
    s.send(b'\r')
    s.type(b'q'); s.finish(timeout=20)
    ctx.common_checks(s, 0, problems)
    bank = list(root.glob('note-*.wav'))
    whole = list(root.glob('whole-*.wav'))
    if len(bank) != 48: problems.append('full editor bank plus cadence sharps missing')
    if not whole: problems.append('hear did not render both voices')
    for path in bank + whole:
        data = path.read_bytes()
        if data[:4] != b'RIFF' or data[8:12] != b'WAVE': problems.append('not WAV: '+path.name)
        if struct.unpack_from('<HHI', data, 20) != (1, 2, 48000): problems.append('wrong PCM format')
        if len(set(data[44:])) <= 1: problems.append('silent synthesis: '+path.name)
    if not s.err.count(b'wav-sink') and not Path('/usr/bin/afplay').exists():
        problems.append('Linux audition did not reach the WAV sink')
    print(untraced(s.err))
    return s, problems

def quit_screen(bin, ctx, keys):
    s = paced(ctx, [bin, '--mute'], 24, 80, ctx.env_for())
    for k in keys: s.send(k)
    s.type(b'q'); s.finish(); problems = []
    ctx.common_checks(s, 0, problems)
    return s, problems

def title_quit(bin, ctx): return quit_screen(bin, ctx, [])
def staff_quit(bin, ctx): return quit_screen(bin, ctx, [b'\r'])
def card_quit(bin, ctx): return quit_screen(bin, ctx, [b'\r',b'\r'])
def escape(bin, ctx):
    s=paced(ctx,[bin,'--mute'],24,80,ctx.env_for())
    # A lone ESC is resolved by the game's own 50 ms timeout, then quits.
    s.type(b'\x1b',0);s.finish();problems=[]
    ctx.common_checks(s,0,problems)
    return s,problems

ROWS={'editor-ear':editor,'title-quit':title_quit,'staff-quit':staff_quit,'card-quit':card_quit,'escape':escape}


def solved_record(bin, ctx):
    root=Path(ctx.ROOT)/'target/pty'
    path=root/'solved.pk'
    s=paced(ctx,[bin,'--mute','--record',str(path)],24,80,ctx.env_for())
    s.send(b'\r')
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','check':b'\r'}
    ack=None
    for line in (Path(ctx.ROOT)/'tests/cases/preset-1-80.pk').read_text().splitlines():
        words=line.split()
        if words and words[0]=='t' and words[-1] in keys:ack=s.send(keys[words[-1]])
    problems=[]
    if 'Legal    3 / 3 stars' not in screen(bin,ctx,s,ack):problems.append('reference did not reach the three-star card')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    s.verify(path,'solved-record',problems)
    text=path.read_text()
    if '# score 3' not in text:problems.append('recorded score is not three')
    ticks=int([line.split()[1] for line in text.splitlines() if line.endswith(' quit')][-1])+1
    p=subprocess.run([bin,'--headless','--script',str(path),'--frames',str(ticks),'--dump',str(root/'record-verify')],capture_output=True,text=True)
    if p.returncode or 'verified score 3' not in p.stderr:problems.append('actual recording did not verify: '+p.stderr)
    return s,problems
ROWS['solved-record']=solved_record


def panel_right_twice(bin, ctx):
    s = paced(ctx, [bin, '--seed', '7', '--no-title', '--mute'], 24, 80, ctx.env_for())
    s.send(b'\x1b[C'); ack = s.send(b'\x1b[C')
    image = screen(bin, ctx, s, ack).splitlines()
    problems = []
    if 'Editing bar 3' not in image[4][58:]:
        problems.append('selected-bar panel did not become Editing bar 3')
    if 'Breaks: bar 3' not in image[16][58:]:
        problems.append('diagnostics did not follow the selected bar')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    return s, problems


def hear_whole_is_played(bin, ctx):
    import hashlib
    import re
    root = Path(ctx.ROOT) / 'target/pty/hear-whole'
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'whole-1.wav'
    if path.exists(): path.unlink()
    env = ctx.env_for(); env['FUGUE_WAV_DIR'] = str(root); env['FUGUE_AUDIO_TRACE'] = '1'
    s = paced(ctx, [bin, '--seed', '7', '--no-title'], 24, 80, env)
    problems = []
    s.send(b'h')
    # h renders the whole WAV before its carrying frame; the bound is liveness.
    deadline = time.monotonic() + 15
    while not path.exists() and time.monotonic() < deadline: s.pump(.1)
    if not path.exists(): problems.append('h did not render the whole WAV')
    else:
        data = path.read_bytes(); pcm = data[44:]
        duration = len(pcm) / 192000
        if abs(duration - 10) > 1/30: problems.append(f'whole duration {duration} is not ten bars')
        digest = hashlib.sha256(pcm).hexdigest()
        expected = (Path(ctx.ROOT)/'tests/goldens/audio/whole-seed7.sha256').read_text().strip()
        if digest != expected: problems.append(f'whole PCM differs: {digest}')
        if not any(pcm): problems.append('whole PCM is silent')
        print(f'whole WAV {path} duration {duration:.6f}s PCM sha256 {digest}')
    mac = Path('/usr/bin/afplay').exists()
    if mac:
        matches = re.findall(rb'player-start pid (\d+) slot (\d+) ([^\r\n]+whole-1.wav)', s.err)
        if not matches: problems.append('h rendered but never started afplay')
        else:
            pid, slot, _ = matches[-1]; pid = int(pid)
            live = subprocess.run(['ps','-p',str(pid),'-o','ppid=,comm=,args='], capture_output=True, text=True).stdout
            print(f'afplay appearing pid {pid}: {live.strip()}')
            if '/usr/bin/afplay' not in live or str(path) not in live or int(live.split()[0]) != s.job:
                problems.append('whole player is not the owned afplay child')
            deadline = time.monotonic() + 14
            end = b'player-end slot '+slot+b' status 0'
            while end not in s.err and time.monotonic() < deadline: s.pump(.1)
            gone = subprocess.run(['ps','-p',str(pid),'-o','pid='], capture_output=True, text=True)
            print(f'afplay ended pid {pid}: ps exit {gone.returncode}, owner reaped {end in s.err}')
            if end not in s.err or gone.returncode == 0: problems.append('whole afplay child did not end and reap')
    else:
        whole_sink = any(b'wav-sink' in line and b'whole-1.wav' in line for line in s.err.splitlines())
        if not whole_sink: problems.append('h rendered but never handed whole WAV to output')
        sinks = list(root.glob('audition-*.wav'))
        if not sinks or sinks[-1].read_bytes() != path.read_bytes(): problems.append('whole WAV did not reach the Linux sink intact')
    s.type(b'q'); s.finish(timeout=20); ctx.common_checks(s, 0, problems)
    print(untraced(s.err))
    return s, problems

ROWS['panel-right-twice'] = panel_right_twice
ROWS['hear-whole-is-played'] = hear_whole_is_played
# The old rows waited 11 s of wall time for a ten-bar hearing to end; the
# same wait in the game's own ticks, counted from h's carrying frame.
HEARING_TICKS = 330


def rhythmic_record(bin, ctx, book):
    """Record ordinary editor keys, hear the rhythm, then verify the recorded score."""
    root = Path(ctx.ROOT) / 'target/pty'
    path = root / f'book-{book}-solved.pk'
    env = ctx.env_for()
    env['FUGUE_STATE'] = str(root / f'book-{book}-state')
    s = paced(ctx, [bin, '--book', str(book), '--mute', '--record', str(path)], 24, 80, env)
    s.send(b'\r')
    keys = {'up': b'\x1b[A', 'down': b'\x1b[B', 'right': b'\x1b[C', 'sharp': b'#'}
    source = Path(ctx.ROOT) / f'tests/cases/book-{book}-preset-1-80.pk'
    batch = b''.join(keys[line.split()[-1]] for line in source.read_text().splitlines()
                     if line.startswith('t 1 '))
    s.send(batch)
    hear = s.send(b'h')
    s.until(hear['frame'] + HEARING_TICKS)
    ack = s.send(b'\r')
    problems = []
    if 'Legal    3 / 3 stars' not in screen(bin, ctx, s, ack):
        problems.append(f'Book {book}: ordinary inputs did not reach a three-star card')
    s.type(b'q'); s.finish()
    ctx.common_checks(s, 0, problems)
    if not path.exists():
        problems.append('no rhythmic recording')
        return s, problems
    s.verify(path, f'book-{book}-record', problems)
    text = path.read_text()
    if '# score 3' not in text:
        problems.append('recorded rhythmic score is not three')
    ticks = max(int(line.split()[1]) for line in text.splitlines() if line.startswith('t ')) + 1
    p = subprocess.run([bin, '--headless', '--script', str(path), '--frames', str(ticks),
                        '--every', str(ticks), '--dump', str(root / f'book-{book}-verify'), '--mute'],
                       capture_output=True, text=True, timeout=30)
    if p.returncode or 'verified score 3' not in p.stderr:
        problems.append('rhythmic recording did not verify: ' + p.stderr)
    saved = Path(env['FUGUE_STATE'])
    if not saved.exists() or saved.read_text().split()[book + 1] != '3':
        problems.append('best stars were not saved for the selected book')
    return s, problems


for _book in range(2, 6):
    ROWS[f'book-{_book}-record'] = lambda bin, ctx, book=_book: rhythmic_record(bin, ctx, book)


def rhythmic_ear(bin, ctx):
    root = Path(ctx.ROOT) / 'target/pty/rhythmic-audio'
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True)
    env = ctx.env_for()
    env['FUGUE_WAV_DIR'] = str(root)
    env['FUGUE_AUDIO_TRACE'] = '1'
    env['FUGUE_STATE'] = str(root / 'progress')
    s = paced(ctx, [bin, '--book', '5', '--no-title'], 24, 80, env)
    s.send(b'h')
    deadline = time.monotonic() + 20
    while not list(root.glob('whole-*.wav')) and time.monotonic() < deadline: s.pump(.1)
    s.type(b'q'); s.finish(timeout=20)
    problems = []
    ctx.common_checks(s, 0, problems)
    files = list(root.glob('whole-*.wav'))
    if not files: problems.append('rhythmic h produced no WAV')
    for path in files:
        data = path.read_bytes()
        if len(data) != 44 + 10 * 192000: problems.append('rhythmic WAV duration differs from ten bars')
        if len(set(data[44:])) <= 1: problems.append('rhythmic WAV is silent')
    if b'whole-render' not in s.err: problems.append('rhythmic score never reached the output owner')
    return s, problems


ROWS['book-5-ear'] = rhythmic_ear


def ledger_below_and_back(bin, ctx):
    s = paced(ctx, [bin, '--no-title', '--mute'], 24, 80, ctx.env_for())
    ack = s.send(b'\x1b[B'*8)
    image = screen(bin, ctx, s, ack).splitlines()
    problems = []
    matches = [row for row in image if row[1:4].strip() == 'F3']
    if not matches or not any('*' in row[8:11] or '●' in row[8:11] for row in matches):
        problems.append('three-ledger F3 not visible below treble')
    for name in ['C4', 'A3', 'F3']:
        row = next((row for row in image if row[1:4].strip() == name), '')
        if not row or not any(c in '-─' for c in row[8:11]): problems.append('missing ledger '+name)
    ack = s.send(b'\x1b[A'*8)
    image = screen(bin, ctx, s, ack).splitlines()
    if 'G4' not in image[8][58:]: problems.append('walk did not return to G4')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    return s, problems


def selected_event_status(bin, ctx):
    s = paced(ctx, [bin, '--book', '3', '--no-title', '--mute'], 24, 80, ctx.env_for())
    # Give five adjacent events distinct pitches using only ordinary input.
    for n in range(1, 6):
        s.send(b'\x1b[A'*n)
        if n < 5: s.send(b'\x1b[C')
    ack = s.send(b'\x1b[D'*4)
    problems = []
    expected = ['M6 imperfect', 'M7 dissonant', 'P8 perfect', 'M9 dissonant', 'm10 imperfect']
    for i, interval in enumerate(expected):
        image = screen(bin, ctx, s, ack).splitlines()
        bar, beat = i//4+1, (i%4)*2+1
        if f'Bar {bar}, beat {beat}:8' not in image[5][58:]: problems.append(f'stale cursor status at event {i}: '+image[5])
        if interval not in image[7][58:]: problems.append(f'stale interval at event {i}: '+image[7])
        if i < 4: ack = s.send(b'\x1b[C')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    return s, problems


def edit_florid_bar(bin, ctx):
    path = Path(ctx.ROOT)/'target/pty/edited-rhythm.pk'
    s = paced(ctx, [bin, '--book', '5', '--no-title', '--mute', '--record', str(path)], 24, 80, ctx.env_for())
    ack = s.send(b'r[.')
    image = screen(bin, ctx, s, ack)
    problems = []
    if '/4.' not in image or '[ split ] join . dot t tie r rest' not in image: problems.append('dot or rhythm hint absent')
    s.send(b'u]trr')
    ack = s.send(b'\r')
    if 'Not yet' not in screen(bin, ctx, s, ack): problems.append('edited rhythm was not re-judged')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    s.verify(path, 'book-5-rhythm-edits', problems)
    source = path.read_text()
    if '# score 0' not in source: problems.append('edited rhythm score not recorded')
    ticks = max(int(line.split()[1]) for line in source.splitlines() if line.startswith('t '))+1
    p = subprocess.run([bin, '--headless', '--script', str(path), '--frames', str(ticks), '--every', str(ticks), '--dump', str(path.parent/'edited-verify')], capture_output=True, text=True)
    if p.returncode or 'verified score 0' not in p.stderr: problems.append('edited rhythm did not replay with same verdict')
    return s, problems

ROWS['three-ledgers-below-and-back'] = ledger_below_and_back
ROWS['selected-event-status'] = selected_event_status
ROWS['book-5-rhythm-edits'] = edit_florid_bar


def cursor_same_frame(bin, ctx):
    return runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-check.py'))['check'](bin, ctx)


ROWS['cursor-same-frame'] = cursor_same_frame


def event_caret(bin, ctx):
    return runpy.run_path(str(Path(ctx.ROOT)/'tools/event-caret.py'))['check'](bin, ctx)


ROWS['event-caret'] = event_caret


def quiet_audio_page_change(bin, ctx):
    root = Path(ctx.ROOT)/'target/pty/quiet-audio-page-change'
    root.mkdir(parents=True, exist_ok=True)
    env = ctx.env_for()
    env['FUGUE_SOUND'] = '1'
    env['FUGUE_AUDIO_TRACE'] = '0'
    # A real player's stderr shares the terminal. The ordinary runner pipes it
    # away; this exec keeps the same foreground job while joining both streams.
    # So this session carries no --trace: each key is acknowledged by the
    # exact replayed frame instead (tests/paced.py's await_state).
    s = PACED['tracked'](ctx)(['/bin/sh', '-c', 'exec "$@" 2>&1', 'merged-audio', bin,
                     '--book', '5', '--no-title'], 24, 80, env, 0.0)
    head = PACED['header'](5, '80x24', 'rich')
    PACED['await_state'](s, bin, root, PACED['replayed'](bin, root, head, [], '80x24'), '80x24', 'the first page')
    s.type(b'n', 0)
    problems = []
    try:
        PACED['await_state'](s, bin, root, PACED['replayed'](bin, root, head, ['new'], '80x24'), '80x24', 'the next page')
    except AssertionError as e:
        problems.append(str(e))
    s.type(b'q'); s.finish()
    ctx.common_checks(s, 0, problems)
    after_enter = s.out.split(b'\x1b[?1049h', 1)[-1]
    if b'note-bank render_us' in after_enter:
        problems.append('normal page change leaked note-bank diagnostics into the drawn terminal')
    return s, problems


def cached_arrow_auditions(bin, ctx):
    root = Path(ctx.ROOT)/'target/pty/cached-arrow-auditions'
    root.mkdir(parents=True, exist_ok=True)
    env = ctx.env_for()
    env['FUGUE_SOUND'] = '1'
    env['FUGUE_AUDIO_TRACE'] = '1'
    env['FUGUE_WAV_DIR'] = str(root)
    s = paced(ctx, [bin, '--book', '5', '--no-title'], 24, 80, env)
    before = {p.name: p.stat().st_mtime_ns for p in root.glob('note-*.wav')}
    # Rest aside, edit the next sounding held event using ordinary arrow bytes.
    s.send(b'\x1b[C'*4)
    for _ in range(10):
        s.send(b'\x1b[A')
        s.send(b'\x1b[B')
    s.type(b'q'); s.finish()
    problems = []
    ctx.common_checks(s, 0, problems)
    if s.err.count(b'note-bank render_us') != 1 or b'whole-render' in s.err:
        problems.append('an arrow caused synchronous sound preparation')
    after = {p.name: p.stat().st_mtime_ns for p in root.glob('note-*.wav')}
    if not before or before != after: problems.append('arrows rewrote the prepared note bank')
    starts = s.err.count(b'player-start') + s.err.count(b'wav-sink')
    if starts != 20: problems.append(f'only {starts}/20 cached auditions reached output')
    return s, problems


ROWS['quiet-audio-page-change'] = quiet_audio_page_change
ROWS['cached-arrow-auditions'] = cached_arrow_auditions


def cursor_long(bin, ctx):
    return runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-long.py'))['check'](bin, ctx)


ROWS['cursor-long'] = cursor_long

# The old row let the one-second audition cues finish with 1.1 s of wall time;
# the same wait in the game's ticks. The exposition's entries were read 6.2 s
# and 12.4 s after h: the same, in ticks from h's carrying frame.
AUDITIONS_TICKS = 33
ENTRY_TICKS = 186

def fugue_record(bin, ctx, index=1):
    """The real editor, named entry transition, PCM handoff and score recording."""
    import hashlib
    root=Path(ctx.ROOT)/'target/pty/fugue';root.mkdir(parents=True,exist_ok=True)
    record=root/f'book-6-{index}-solved.pk'
    env=ctx.env_for();env['FUGUE_STATE']=str(root/f'state-{index}')
    audio=index==1
    if audio:
        env['FUGUE_WAV_DIR']=str(root);env['FUGUE_AUDIO_TRACE']='1'
        path=root/'whole-1.wav'
        if path.exists(): path.unlink()
    case=Path(ctx.ROOT)/f'tests/cases/book-6-preset-{index}-80.pk'
    argv=[bin,'--book','6','--record',str(record)]
    if not audio: argv.append('--mute')
    s=paced(ctx,argv,24,80,env);problems=[]
    if audio and b'note-bank render_us' not in s.err:problems.append('fugue note bank did not prepare')
    s.send(b'\r')
    for _ in range(index-1):s.send(b'n')
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v'}
    actions=[keys[line.split()[-1]] for line in case.read_text().splitlines() if line.startswith('t 1 ')]
    if audio:
        for key in actions: last=s.send(key)
        s.until(last['frame']+AUDITIONS_TICKS)  # the owned one-second audition cues finish before whole-piece playback
    else:
        s.send(b''.join(actions))
    if audio:
        hear=s.send(b'h')
        deadline=time.monotonic()+20
        while not path.exists() and time.monotonic()<deadline:s.pump(.1)
        if not path.exists():problems.append('fugue h did not render an exposition')
        else:
            pcm=path.read_bytes()[44:]
            digest=hashlib.sha256(pcm).hexdigest()
            expected=(Path(ctx.ROOT)/'tests/goldens/audio/exposition-1.sha256').read_text().strip()
            if len(pcm)!=12*192000 or digest!=expected:problems.append(f'played exposition PCM differs: {len(pcm)} {digest}')
        if 'Subject' not in screen(bin,ctx,s,hear):problems.append('subject entry is not named')
        # The audible timeline starts only after rendering and output handoff.
        s.until(hear['frame']+ENTRY_TICKS)
        later=ctx.screen_text(bin,s.frame(next(t for t,_,_,_ in s.outputs if t>=hear['frame']+ENTRY_TICKS)))
        if 'Answer' not in later or 'Countersubject' not in later:problems.append('answer and continuation entries are not named')
        s.until(hear['frame']+2*ENTRY_TICKS)
        if Path('/usr/bin/afplay').exists():
            import re
            starts=list(re.finditer(rb'player-start pid (\d+) slot (\d+) [^\r\n]*whole-1.wav',s.err))
            if not starts:problems.append('owned exposition player did not start')
            else:
                start=starts[-1]; end=b'player-end slot '+start.group(2)+b' status 0'
                deadline=time.monotonic()+4
                while end not in s.err[start.end():] and time.monotonic()<deadline:s.pump(.1)
                if end not in s.err[start.end():]:problems.append('owned exposition player did not reap after its own start')
        elif not any(b'wav-sink' in line and b'whole-1.wav' in line for line in s.err.splitlines()):
            problems.append('played exposition never reached the Linux sink')
    ack=s.send(b'\r')
    if 'Legal exposition    3 / 3 stars' not in screen(bin,ctx,s,ack):problems.append('fugue editor did not reach three stars')
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    if not record.exists():problems.append('fugue recording absent')
    else:
        s.verify(record,f'fugue-record-{index}',problems)
        text=record.read_text()
        if '# score 3' not in text:problems.append('recorded fugue score is not three')
        last=max(int(line.split()[1]) for line in text.splitlines() if line.startswith('t '))
        r=subprocess.run([bin,'--headless','--script',str(record),'--frames',str(last+1),'--every',str(last+1),'--dump',str(root/f'verify-{index}'),'--mute'],capture_output=True,text=True,timeout=45)
        if r.returncode or 'verified score 3' not in r.stderr:problems.append('actual fugue recording did not verify: '+r.stderr)
    print(untraced(s.err))
    return s,problems


def fugue_end(bin,ctx):
    root=Path(ctx.ROOT)/'target/pty/fugue';root.mkdir(parents=True,exist_ok=True)
    state=root/'end-state'
    if state.exists():state.unlink()
    env=ctx.env_for();env['FUGUE_STATE']=str(state)
    s=paced(ctx,[bin,'--book','6','--mute'],24,80,env)
    ack=s.send(b'\r')
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v','check':b'\r','new':b'n'}
    events=(Path(ctx.ROOT)/'tests/cases/book-6-end-80.pk').read_text().splitlines()
    for tick in range(1,9):
        batch=b''.join(keys[line.split()[-1]] for line in events if line.startswith(f't {tick} '))
        if batch:ack=s.send(batch)
    problems=[];image=screen(bin,ctx,s,ack)
    if 'The sixth book is lit' not in image or '3 + 3 + 3 = 9 / 9' not in image:problems.append('three played tutorials did not reach the end card')
    ack=s.send(b'b')
    if 'VI. The fugue  [3*]' not in screen(bin,ctx,s,ack):problems.append('sixth title book did not light')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    if not state.exists() or state.read_text().split()[7]!='3':problems.append('sixth-book completion did not persist')
    return s,problems

ROWS['fugue-exposition-record']=fugue_record
ROWS['fugue-two-desks-record']=lambda bin,ctx:fugue_record(bin,ctx,3)
ROWS['fugue-end-card']=fugue_end


def fugue_junk_screen(bin, ctx, width=120, tier='rich'):
    """The terminal owns stderr too; compare every glyph and style after repaint.

    stderr shares the terminal here, so the session cannot carry --trace: each
    key is acknowledged by the exact complete headless state instead, awaited
    with the injector's liveness bound, never a fixed settle."""
    import sys
    root=Path(ctx.ROOT)/f'target/pty/fugue-junk-{width}-{tier}'
    root.mkdir(parents=True,exist_ok=True)
    height=24 if width==80 else 40
    wrapper=root/'launch.py'
    wrapper.write_text('''import os,sys
w,h=int(sys.argv[1]),int(sys.argv[2])
os.write(1,b"\\x1b[?1049h\\x1b[41;97m")
for row in range(h):
    os.write(1,f"\\x1b[{row+1};1H".encode()+b"J"*w)
os.write(1,b"\\x1b[0m\\x1b[H")
os.dup2(1,2)
os.execve(sys.argv[3],sys.argv[3:],os.environ)
''')
    env=ctx.env_for();env['FUGUE_STATE']=str(root/'state');env['FUGUE_WAV_DIR']=str(root/'audio')
    s=PACED['tracked'](ctx)([sys.executable,'-I',str(wrapper),str(width),str(height),bin,'--book','6','--no-title','--size',f'{width}x{height}','--tier',tier],height,width,env,0.0)
    events=[];problems=[]
    def expected(name,frames):
        script=root/f'{name}.pk'
        script.write_text(f'pk 1\nseed 0\ntier {tier}\nsize {width}x{height}\nstart 22001\n'+''.join(f't 1 {key}\n' for key in events))
        made=subprocess.run([bin,'--headless','--script',str(script),'--frames',str(frames),'--every',str(frames),'--dump',str(root/name),'--mute'],capture_output=True,text=True,timeout=30)
        if made.returncode:
            problems.append(name+' headless command failed');return None
        return (root/name/'final.txt').read_text(),(root/name/'final.sty').read_text()
    def state():
        cap=root/'state.bin'
        cap.write_bytes(s.out)
        got=subprocess.run([bin,'--apply',str(cap),'--size',f'{width}x{height}'],capture_output=True,text=True,timeout=30)
        if got.returncode:return None
        text,styles,_=got.stdout.split('--\n')
        return text,styles
    def compare(name,frames=2,leave=None):
        want=expected(name,frames)
        if want is None:return
        # Sound preparation can outlive any fixed settle on a busy host. Await
        # this exact complete state, never a masked region or arbitrary output
        # activity. Persistent stderr/repaint damage still fails. Live key
        # latency remains independently gated by fugue-press-budget.
        began=time.monotonic();deadline=began+PACED['LIVENESS_S'];attempts=0
        if leave is not None:
            # A state the key leaves first (the hearing's own frames): the
            # key has been read only once the screen has left it.
            while state()==leave and time.monotonic()<deadline:s.pump(.05)
        while True:
            got=state()
            good=got==want
            if good or time.monotonic()>=deadline:break
            if attempts==0:(root/f'{name}-initial.bin').write_bytes(s.out)
            attempts+=1;s.pump(.05)
        text,styles=got if got else ('','')
        glyphs=sum(a!=b for a,b in zip(text,want[0]))+abs(len(text)-len(want[0]))
        print(f'fugue junk {width}x{height} {tier} {name}: {width*height} cells, glyph differences {glyphs}, styles equal {styles==want[1]}, state wait {time.monotonic()-began:.3f}s ({attempts} retries)')
        if not good:problems.append(f'{name}: terminal differs from complete headless frame ({glyphs} glyph cells, styles {styles==want[1]})')
        if tier=='rich':
            grain=sum(int(token.rsplit('*',1)[1]) for line in want[1].splitlines() for token in line.split() if token.split(',')[1]=='223')
            print(f'fugue deliberate grain cells: {grain}')
        return want
    current=compare('first')
    for name,raw,keys in [('page-2',b'n',['new']),('page-3',b'n',['new']),('voice',b'v',['voice-switch']),('refusal',b'[[.',['split','split','dot'])]:
        s.type(raw,0);events.extend(keys);current=compare(name)
    s.type(b'h',0);events.append('hear');compare('after-hear',400,leave=current)
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    return s,problems


def fugue_press_budget(bin, ctx, book=6):
    """Record read-to-carrying-frame latency, including Book VI h preparation."""
    import math
    root=Path(ctx.ROOT)/f'target/pty/fugue-press-budget-{book}';root.mkdir(parents=True,exist_ok=True)
    env=ctx.env_for();env['FUGUE_STATE']=str(root/'state');env['FUGUE_WAV_DIR']=str(root/'audio')
    s=paced(ctx,[bin,'--book',str(book),'--no-title'],24,80,env);problems=[];rows=[]
    for name,raw in [('right',b'\x1b[C'),('right',b'\x1b[C'),('left',b'\x1b[D'),('up',b'\x1b[A'),('down',b'\x1b[B'),('hear',b'h')]:
        ack=s.send(raw)
        tick,micros=ack['frame'],ack['inner_us']
        if micros is None:problems.append('no carrying frame for '+name);continue
        frames=math.ceil(micros/(1000000/30))
        row=f'{name}: frame {tick}, read-to-frame {micros} us, {frames} frame budgets';rows.append(row);print(row)
    (root/'measurements.txt').write_text('\n'.join(rows)+'\n')
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    return s,problems

for _width in (80,120):
    for _tier in ('plain','rich'):
        ROWS[f'fugue-junk-{_width}-{_tier}']=lambda bin,ctx,width=_width,tier=_tier:fugue_junk_screen(bin,ctx,width,tier)
ROWS['fugue-press-budget']=fugue_press_budget


def fugue_cursor_panel(bin, ctx, width=120):
    root=Path(ctx.ROOT)/f'target/pty/fugue-cursor-{width}';root.mkdir(parents=True,exist_ok=True)
    height=24 if width==80 else 40
    env=ctx.env_for();env['FUGUE_STATE']=str(root/'state')
    s=paced(ctx,[bin,'--book','6','--no-title','--mute','--size',f'{width}x{height}'],height,width,env)
    s.send(b'nn')
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v'}
    source=(Path(ctx.ROOT)/f'tests/cases/book-6-preset-3-{width}.pk').read_text()
    s.send(b''.join(keys[x.split()[-1]] for x in source.splitlines() if x.startswith('t 1 ')))
    s.send(b'v')
    # Break the answer in bar 3, then inspect a different bar before returning.
    ack=s.send(b'\x1b[C'*4+b'#'+b'\x1b[D'*4)
    problems=[]
    def expect(label,bar,beat,pitch,figure=None):
        path=root/(label+'.bin');path.write_bytes(s.frame(ack['frame']))
        result=subprocess.run([bin,'--apply',str(path),'--size',f'{width}x{height}'],capture_output=True,text=True,timeout=30)
        if result.returncode:problems.append(label+' apply failed');return
        screen=result.stdout.split('--\n')[0].splitlines(); margin=width-22
        panel=[line[margin:] for line in screen]
        if f'Editing bar {bar}' not in panel[4] or f'Bar {bar}, beat {beat}:8' not in panel[5]:problems.append(label+' stale bar/beat: '+repr(panel[4:6]))
        if pitch not in panel[8]:problems.append(label+' stale selected pitch: '+panel[8])
        if figure and figure not in panel[9]:problems.append(label+' stale figure: '+panel[9])
        if f'Breaks: bar {bar}' not in panel[16]:problems.append(label+' wrong diagnostic heading')
        for row in panel[12:]:
            if 'bar ' in row and ' - ' in row and f'bar {bar} - ' not in row:problems.append(label+' finding from another bar: '+row)
        if bar==3 and not any('bar 3 -' in row for row in panel[12:]):problems.append(label+' missing active-bar findings')
        print(f'fugue cursor {width} {label}: bar {bar}, beat {beat}, {pitch}')
    expect('answer-first',1,1,'F5','tonal-mutation')
    ack=s.send(b'\x1b[C'*2);expect('answer-second',2,1,'D5','exact-answer')
    ack=s.send(b'\x1b[C'*2);expect('answer-third',3,5,'Fb5','answer-transposition')
    ack=s.send(b'v');expect('counter-first',1,1,'A4','consonance')
    ack=s.send(b'\x1b[C'*2);expect('counter-second',2,1,'B4','consonance')
    ack=s.send(b'\x1b[C'*2);expect('counter-third',3,5,'D5')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    return s,problems

ROWS['fugue-cursor-panel-80']=lambda bin,ctx:fugue_cursor_panel(bin,ctx,80)
ROWS['fugue-cursor-panel-120']=lambda bin,ctx:fugue_cursor_panel(bin,ctx,120)


def fugue_cursor_motion(bin, ctx, cases=None):
    """Actual first-carrying-frame caret alignment, including held-note offsets.

    Every press is typed through tests/paced.py: the two nine-press runs are
    one press a tick (30 Hz) by the game's trace, each acknowledged by its
    carrying frame and judged at that frame's exact output boundary; each
    recorded key is placed in the first carrying frame after its record tick."""
    import os,json
    root=Path(ctx.ROOT)/'target/pty/fugue-cursor-motion';root.mkdir(parents=True,exist_ok=True)
    if cases is None:cases=[(desk,width,tier,mute) for desk in (0,1) for width in (80,120) for tier in ('rich','plain') for mute in (False,True)]
    problems=[];journal=[];last=None
    lengths=[4,4,8,4,4,4,2,2,8,8]
    for desk,width,tier,mute in cases:
        height=24 if width==80 else 40
        name=f'{desk}-{width}-{tier}-'+('mute' if mute else 'sound');path=root/(name+'.pk')
        env=ctx.env_for();env['FUGUE_STATE']=str(root/(name+'.state'));env['FUGUE_WAV_DIR']=str(root/(name+'-audio'))
        s=paced(ctx,[bin,'--book','6','--no-title','--size',f'{width}x{height}','--tier',tier,'--record',str(path)]+(['--mute'] if mute else []),height,width,env)
        last=s;s.send(b'nn')
        if desk:s.send(b'v')
        initial=s.frame()
        for key in (b'\x1b[C',b'\x1b[D'):s.send(key)
        for key in (b'\x1b[C',b'\x1b[D'):s.burst(key,9)
        s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
        recorded=s.verify(path,name,problems)
        events=[(t,k) for t,k in recorded if k in ('left','right')]
        if [key for _,key in events]!=['right','left']+['right']*9+['left']*9:problems.append(name+' lost or reordered key')
        press_of={}
        for i,(t,k) in enumerate(recorded):
            if k in ('left','right'):press_of[i]=len(press_of)
        def image(data):
            cap=root/'frame.bin';cap.write_bytes(data)
            out=subprocess.run([bin,'--apply',str(cap),'--size',f'{width}x{height}'],capture_output=True,text=True,check=True)
            return out.stdout.split('--\n')[0].splitlines()
        def caret(screen):return [(y,x) for y,row in enumerate(screen) for x,ch in enumerate(row[:width-24]) if ch=='^']
        previous=caret(image(initial));event_index=0;previous_first=0;records=[];unit=1 if desk else 2
        by_frame=PACED['carrying_frames'](recorded,[c[0] for c in s.carrying])
        for tick in sorted(by_frame):
            keys=[(press_of[i],key) for i,_,key in by_frame[tick] if i in press_of]
            if not keys:continue
            for _,key in keys:event_index+=1 if key=='right' else -1
            position=sum(lengths[:event_index])
            widths=[max(6 if n==8 else 5 if n==4 else 4,(n+unit-1)//unit) for n in lengths]
            onsets=[sum(lengths[:i]) for i in range(len(lengths))]
            def column(first):
                x=9
                for i in range(event_index):
                    if onsets[i]<first*8:continue
                    x+=widths[i]
                    if (onsets[i]+lengths[i])%8==0:x+=1
                return x
            first=0
            while first<position//8 and column(first)+widths[event_index]-2>=width-27:first+=1
            expected=column(first)
            screen=image(s.frame(tick));current=caret(screen)
            panel=f'Bar {position//8+1}, beat {position%8+1}:8' in screen[5][width-22:]
            aligned=len(current)==1 and current[0][1]==expected
            moved=bool(current) and current!=previous
            scrolled=first!=previous_first
            for i,key in keys:records.append({'press':i+1,'key':key,'frame':tick,'panel_frames':1 if panel else None,'caret_frames':1 if aligned and (moved or scrolled) else None,'editable_event':event_index+1,'first_bar':first+1,'scrolled':scrolled,'caret':current,'expected_x':expected,'coalesced':len(keys)})
            if not panel or not aligned or not (moved or scrolled):problems.append(f'{name} press {keys[0][0]+1}: panel {panel}, caret {current}, expected x {expected}, moved {moved}')
            previous=current;previous_first=first
        if len(records)!=20:problems.append(name+f' only {len(records)} accounted presses')
        late=s.lateness()
        journal.append({'case':name,'presses':records,'late_ticks':late,'acks':s.acks})
        print(f'fugue caret {name}: {sum(r["caret_frames"]==1 for r in records)}/20 aligned in first carrying frame; 30 Hz by the trace, late ticks max {max(late,default=0)}')
    (root/'journal.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last,problems

ROWS['fugue-cursor-same-frame']=fugue_cursor_motion


def fugue_right_then_up(bin, ctx, Session=None):
    """The maintainer's exact opening command; identify the event actually edited."""
    import json
    root=Path(ctx.ROOT)/'target/pty/fugue-right-up';root.mkdir(parents=True,exist_ok=True)
    env=ctx.env_for();env['FUGUE_STATE']=str(root/'state');env['FUGUE_WAV_DIR']=str(root/'audio')
    expected=root/'initial-expected'
    subprocess.run([bin,'--book','6','--size','120x40','--no-title','--headless',
                    '--mute','--frames','1','--every','1','--dump',str(expected)],
                   env=env,capture_output=True,check=True,timeout=30)
    wanted=((expected/'final.txt').read_text(),(expected/'final.sty').read_text())
    began=time.monotonic()
    s=(Session or PACED['session'](ctx))([bin,'--book','6','--size','120x40','--no-title','--trace'],40,120,env)
    # Alternate-screen entry precedes the 150-ms keyboard negotiation; the
    # game's first traced frame is its complete initial frame. Nothing is
    # typed before it.
    first=s.ready()
    ready=PACED['applied'](bin,root,s.frame(first),'120x40')==wanted
    problems=[];journal={}
    print(f'VI initial complete frame: {ready}, first traced frame {first}, wait {time.monotonic()-began:.3f}s')
    if not ready:
        (root/'initial-not-ready.bin').write_bytes(s.frame(first))
        problems.append('Book VI never drew its exact complete initial frame before input')
        s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
        return s,problems
    def capture(name,ack=None):
        data=s.frame(first if ack is None else ack['frame'])
        cap=root/(name+'.bin');cap.write_bytes(data)
        result=subprocess.run([bin,'--apply',str(cap),'--size','120x40'],capture_output=True,text=True,check=True)
        text,styles,_=result.stdout.split('--\n');rows=text.splitlines();palette=[]
        for row in styles.splitlines():
            expanded=[]
            for run in row.split():
                style,count=run.split('*');expanded.extend([tuple(map(int,style.split(',')))]*int(count))
            palette.append(expanded)
        heads={x:y for y,row in enumerate(rows) for x,ch in enumerate(row[:96]) if ch in ('*','●') and palette[y][x][0] in (4,24)}
        carets=[(y,x) for y,row in enumerate(rows) for x,ch in enumerate(row) if ch=='^']
        data={'heads':heads,'carets':carets,'pitch_status':rows[8][98:].strip(),'bar_status':rows[5][98:].strip()}
        journal[name]=data;print(f'VI {name}: {data}')
        return data
    initial=capture('initial')
    right=capture('right-once',s.send(b'\x1b[C'))
    up=capture('then-up',s.send(b'\x1b[A'))
    columns=sorted(initial['heads'])
    changed=[x for x in columns if initial['heads'][x]!=up['heads'].get(x)]
    print(f'VI changed event columns {changed}; expected second event {columns[1]}')
    if changed!=[columns[1]]:problems.append('Right then Up changed the wrong event: '+str(changed))
    for name,data in [('initial',initial),('right',right),('up',up)]:
        want=columns[0] if name=='initial' else columns[1]
        if len(data['carets'])!=1 or data['carets'][0][1]!=want:problems.append(name+' caret does not name the editable event')
    if up['pitch_status']!='F4':problems.append('second event did not change E4 to F4')
    # Deliberately wide input isolates overflow markers from the selection caret.
    s.send(b'\x1b[D'*100+b'\x1b[B'*100)
    wide=capture('wide-register',s.send(b'\x1b[C'*100+b'\x1b[A'*100))
    if len(wide['carets'])!=1:problems.append('wide register draws extra cursor glyphs')
    (root/'journal.json').write_text(json.dumps(journal,indent=2)+'\n')
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    return s,problems

def fugue_cold_initial(bin,ctx):
    """Return the pty constructor at entry, while negotiation is still pending."""
    Paced=PACED['session'](ctx)
    class Early(Paced):
        def __init__(self,argv,rows,cols,env,settle=0.3,replies=()):
            self.constructing=True
            super().__init__(argv,rows,cols,env,settle,replies)
            self.constructing=False
        def pump(self,seconds):
            if not getattr(self,'constructing',False):return super().pump(seconds)
            deadline=time.monotonic()+seconds
            while time.monotonic()<deadline:
                super().pump(.001)
                if b'\x1b[?1049h' in self.out:return
    class Cold(ctx):
        @staticmethod
        def env_for():
            env=ctx.env_for();env['FUGUE_SOUND']='0';return env
    return fugue_right_then_up(bin,Cold,Early)

ROWS['fugue-right-then-up']=fugue_right_then_up
ROWS['fugue-cold-initial']=fugue_cold_initial


# Sound-owner rows share the real-pty/restoration runner with the editor rows.
ROWS.update(runpy.run_path(str(Path(__file__).with_name('ear_rows.py')))['ROWS'])
ROWS.update(runpy.run_path(str(Path(__file__).with_name('cantus_rows.py')))['ROWS'])
ROWS.update(runpy.run_path(str(Path(__file__).with_name('enhanced_rows.py')))['ROWS'])
# A row that raises ends the sessions it left running (tests/paced.py).
ROWS = {name: PACED['guarded'](row) for name, row in ROWS.items()}
