"""Editor witnesses use actual terminal bytes and inspect the engine's WAV output."""
from pathlib import Path
import struct
import time
import shutil
import subprocess

def editor(bin, ctx):
    root = Path(ctx.ROOT) / 'target/pty/audio'
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    env = ctx.env_for()
    env['FUGUE_WAV_DIR'] = str(root)
    env['FUGUE_AUDIO_TRACE'] = '1'
    s = ctx.Session([bin, '--seed', '7', '--no-title'], 24, 80, env)
    deadline = time.monotonic() + 15
    while b'note-bank render_us' not in s.err and time.monotonic() < deadline:
        s.pump(.1)
    problems = []
    if b'note-bank render_us' not in s.err:
        problems.append('note bank did not prepare')
    s.type(b'\x1b[A', .2)
    s.type(b'\x1b[B', .2)
    s.type(b'h', .2)
    deadline = time.monotonic() + 15
    while not list(root.glob('whole-*.wav')) and time.monotonic() < deadline:
        s.pump(.1)
    s.pump(.3)
    s.type(b'\r', .2)
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
    print(s.err.decode(errors='replace'))
    return s, problems

def quit_screen(bin, ctx, keys):
    s = ctx.Session([bin, '--mute'], 24, 80, ctx.env_for())
    for k in keys: s.type(k, .1)
    s.type(b'q'); s.finish(); problems = []
    ctx.common_checks(s, 0, problems)
    return s, problems

def title_quit(bin, ctx): return quit_screen(bin, ctx, [])
def staff_quit(bin, ctx): return quit_screen(bin, ctx, [b'\r'])
def card_quit(bin, ctx): return quit_screen(bin, ctx, [b'\r',b'\r'])
def escape(bin, ctx):
    s=ctx.Session([bin,'--mute'],24,80,ctx.env_for())
    s.type(b'\x1b',.2);s.finish();problems=[]
    ctx.common_checks(s,0,problems)
    return s,problems

ROWS={'editor-ear':editor,'title-quit':title_quit,'staff-quit':staff_quit,'card-quit':card_quit,'escape':escape}


def solved_record(bin, ctx):
    root=Path(ctx.ROOT)/'target/pty'
    path=root/'solved.pk'
    s=ctx.Session([bin,'--mute','--record',str(path)],24,80,ctx.env_for())
    s.type(b'\r',.08)
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','check':b'\r'}
    for line in (Path(ctx.ROOT)/'tests/cases/preset-1-80.pk').read_text().splitlines():
        words=line.split()
        if words and words[0]=='t' and words[-1] in keys:s.type(keys[words[-1]],.04)
    screen=ctx.screen_text(bin,s.out)
    problems=[]
    if 'Legal    3 / 3 stars' not in screen:problems.append('reference did not reach the three-star card')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    text=path.read_text()
    if '# score 3' not in text:problems.append('recorded score is not three')
    ticks=int([line.split()[1] for line in text.splitlines() if line.endswith(' quit')][-1])+1
    p=subprocess.run([bin,'--headless','--script',str(path),'--frames',str(ticks),'--dump',str(root/'record-verify')],capture_output=True,text=True)
    if p.returncode or 'verified score 3' not in p.stderr:problems.append('actual recording did not verify: '+p.stderr)
    return s,problems
ROWS['solved-record']=solved_record


def panel_right_twice(bin, ctx):
    s = ctx.Session([bin, '--seed', '7', '--no-title', '--mute'], 24, 80, ctx.env_for())
    s.type(b'\x1b[C', .2); s.type(b'\x1b[C', .2)
    screen = ctx.screen_text(bin, s.out).splitlines()
    problems = []
    if 'Editing bar 3' not in screen[4][58:]:
        problems.append('selected-bar panel did not become Editing bar 3')
    if 'Breaks: bar 3' not in screen[16][58:]:
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
    s = ctx.Session([bin, '--seed', '7', '--no-title'], 24, 80, env)
    problems = []
    deadline = time.monotonic() + 15
    while b'note-bank render_us' not in s.err and time.monotonic() < deadline: s.pump(.1)
    s.type(b'h', .3)
    deadline = time.monotonic() + 15
    while not path.exists() and time.monotonic() < deadline: s.pump(.1)
    s.pump(.2)
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
    print(s.err.decode(errors='replace'))
    return s, problems

ROWS['panel-right-twice'] = panel_right_twice
ROWS['hear-whole-is-played'] = hear_whole_is_played
def rhythmic_record(bin, ctx, book):
    """Record ordinary editor keys, hear the rhythm, then verify the recorded score."""
    root = Path(ctx.ROOT) / 'target/pty'
    path = root / f'book-{book}-solved.pk'
    env = ctx.env_for()
    env['FUGUE_STATE'] = str(root / f'book-{book}-state')
    s = ctx.Session([bin, '--book', str(book), '--mute', '--record', str(path)], 24, 80, env)
    s.type(b'\r', .1)
    keys = {'up': b'\x1b[A', 'down': b'\x1b[B', 'right': b'\x1b[C', 'sharp': b'#'}
    source = Path(ctx.ROOT) / f'tests/cases/book-{book}-preset-1-80.pk'
    batch = b''.join(keys[line.split()[-1]] for line in source.read_text().splitlines()
                     if line.startswith('t 1 '))
    s.type(batch, .4)
    s.type(b'h', .2)
    deadline = time.monotonic() + 11
    while time.monotonic() < deadline:
        s.pump(.1)
    s.type(b'\r', .2)
    problems = []
    screen = ctx.screen_text(bin, s.out)
    if 'Legal    3 / 3 stars' not in screen:
        problems.append(f'Book {book}: ordinary inputs did not reach a three-star card')
    s.type(b'q'); s.finish()
    ctx.common_checks(s, 0, problems)
    if not path.exists():
        problems.append('no rhythmic recording')
        return s, problems
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
    s = ctx.Session([bin, '--book', '5', '--no-title'], 24, 80, env)
    deadline = time.monotonic() + 20
    while b'note-bank render_us' not in s.err and time.monotonic() < deadline: s.pump(.1)
    s.type(b'h', .2)
    deadline = time.monotonic() + 20
    while not list(root.glob('whole-*.wav')) and time.monotonic() < deadline: s.pump(.1)
    s.pump(.2)
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
    s = ctx.Session([bin, '--no-title', '--mute'], 24, 80, ctx.env_for())
    s.pump(.2)
    s.type(b'\x1b[B'*8, .3)
    image = ctx.screen_text(bin, s.out).splitlines()
    problems = []
    matches = [row for row in image if row[1:4].strip() == 'F3']
    if not matches or not any('*' in row[8:11] or '●' in row[8:11] for row in matches):
        problems.append('three-ledger F3 not visible below treble')
    for name in ['C4', 'A3', 'F3']:
        row = next((row for row in image if row[1:4].strip() == name), '')
        if not row or not any(c in '-─' for c in row[8:11]): problems.append('missing ledger '+name)
    s.type(b'\x1b[A'*8, .3)
    image = ctx.screen_text(bin, s.out).splitlines()
    if 'G4' not in image[8][58:]: problems.append('walk did not return to G4')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    return s, problems


def selected_event_status(bin, ctx):
    s = ctx.Session([bin, '--book', '3', '--no-title', '--mute'], 24, 80, ctx.env_for())
    # Give five adjacent events distinct pitches using only ordinary input.
    for n in range(1, 6):
        s.type(b'\x1b[A'*n, .07)
        if n < 5: s.type(b'\x1b[C', .07)
    s.type(b'\x1b[D'*4, .2)
    problems = []
    expected = ['M6 imperfect', 'M7 dissonant', 'P8 perfect', 'M9 dissonant', 'm10 imperfect']
    for i, interval in enumerate(expected):
        image = ctx.screen_text(bin, s.out).splitlines()
        bar, beat = i//4+1, (i%4)*2+1
        if f'Bar {bar}, beat {beat}:8' not in image[5][58:]: problems.append(f'stale cursor status at event {i}: '+image[5])
        if interval not in image[7][58:]: problems.append(f'stale interval at event {i}: '+image[7])
        if i < 4: s.type(b'\x1b[C', .2)
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
    return s, problems


def edit_florid_bar(bin, ctx):
    path = Path(ctx.ROOT)/'target/pty/edited-rhythm.pk'
    s = ctx.Session([bin, '--book', '5', '--no-title', '--mute', '--record', str(path)], 24, 80, ctx.env_for())
    s.type(b'r[.', .3)
    image = ctx.screen_text(bin, s.out)
    problems = []
    if '/4.' not in image or '[ split ] join . dot t tie r rest' not in image: problems.append('dot or rhythm hint absent')
    s.type(b'u]trr', .3)
    s.type(b'\r', .2)
    if 'Not yet' not in ctx.screen_text(bin, s.out): problems.append('edited rhythm was not re-judged')
    s.type(b'q'); s.finish(); ctx.common_checks(s, 0, problems)
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
    import runpy
    return runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-check.py'))['check'](bin, ctx)


ROWS['cursor-same-frame'] = cursor_same_frame


def quiet_audio_page_change(bin, ctx):
    env = ctx.env_for()
    env['FUGUE_SOUND'] = '1'
    env['FUGUE_AUDIO_TRACE'] = '0'
    # A real player's stderr shares the terminal. The ordinary runner pipes it
    # away; this exec keeps the same foreground job while joining both streams.
    s = ctx.Session(['/bin/sh', '-c', 'exec "$@" 2>&1', 'merged-audio', bin,
                     '--book', '5', '--no-title'], 24, 80, env)
    deadline = time.monotonic() + 20
    while b'\x1b[?1049h' not in s.out and time.monotonic() < deadline: s.pump(.05)
    s.type(b'n', 1.0)
    s.type(b'q'); s.finish()
    problems = []
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
    s = ctx.Session([bin, '--book', '5', '--no-title'], 24, 80, env)
    deadline = time.monotonic()+20
    while b'note-bank render_us' not in s.err and time.monotonic() < deadline: s.pump(.02)
    before = {p.name: p.stat().st_mtime_ns for p in root.glob('note-*.wav')}
    # Rest aside, edit the next sounding held event using ordinary arrow bytes.
    s.type(b'\x1b[C'*4, .1)
    for _ in range(10):
        s.type(b'\x1b[A', .05)
        s.type(b'\x1b[B', .05)
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
    import runpy
    return runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-long.py'))['check'](bin, ctx)


ROWS['cursor-long'] = cursor_long

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
    s=ctx.Session(argv,24,80,env);problems=[]
    if audio:
        deadline=time.monotonic()+20
        while b'note-bank render_us' not in s.err and time.monotonic()<deadline:s.pump(.1)
        if b'note-bank render_us' not in s.err:problems.append('fugue note bank did not prepare')
    s.type(b'\r',.15)
    for _ in range(index-1):s.type(b'n',.2)
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v'}
    actions=[keys[line.split()[-1]] for line in case.read_text().splitlines() if line.startswith('t 1 ')]
    if audio:
        for key in actions: s.type(key,.04)
        s.pump(1.1)  # let the owned one-second audition cues finish before whole-piece playback
    else:
        s.type(b''.join(actions),.6)
    if audio:
        s.type(b'h',.3)
        deadline=time.monotonic()+20
        while not path.exists() and time.monotonic()<deadline:s.pump(.1)
        if not path.exists():problems.append('fugue h did not render an exposition')
        else:
            pcm=path.read_bytes()[44:]
            digest=hashlib.sha256(pcm).hexdigest()
            expected=(Path(ctx.ROOT)/'tests/goldens/audio/exposition-1.sha256').read_text().strip()
            if len(pcm)!=12*192000 or digest!=expected:problems.append(f'played exposition PCM differs: {len(pcm)} {digest}')
        screen=ctx.screen_text(bin,s.out)
        if 'Subject' not in screen:problems.append('subject entry is not named')
        # The audible timeline starts only after rendering and output handoff.
        s.pump(6.2)
        screen=ctx.screen_text(bin,s.out)
        if 'Answer' not in screen or 'Countersubject' not in screen:problems.append('answer and continuation entries are not named')
        s.pump(6.2)
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
    s.type(b'\r',.3)
    if 'Legal exposition    3 / 3 stars' not in ctx.screen_text(bin,s.out):problems.append('fugue editor did not reach three stars')
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    if not record.exists():problems.append('fugue recording absent')
    else:
        text=record.read_text()
        if '# score 3' not in text:problems.append('recorded fugue score is not three')
        last=max(int(line.split()[1]) for line in text.splitlines() if line.startswith('t '))
        r=subprocess.run([bin,'--headless','--script',str(record),'--frames',str(last+1),'--every',str(last+1),'--dump',str(root/f'verify-{index}'),'--mute'],capture_output=True,text=True,timeout=45)
        if r.returncode or 'verified score 3' not in r.stderr:problems.append('actual fugue recording did not verify: '+r.stderr)
    print(s.err.decode(errors='replace'))
    return s,problems


def fugue_end(bin,ctx):
    root=Path(ctx.ROOT)/'target/pty/fugue';root.mkdir(parents=True,exist_ok=True)
    state=root/'end-state'
    if state.exists():state.unlink()
    env=ctx.env_for();env['FUGUE_STATE']=str(state)
    s=ctx.Session([bin,'--book','6','--mute'],24,80,env)
    s.type(b'\r',.1)
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v','check':b'\r','new':b'n'}
    events=(Path(ctx.ROOT)/'tests/cases/book-6-end-80.pk').read_text().splitlines()
    for tick in range(1,9):
        batch=b''.join(keys[line.split()[-1]] for line in events if line.startswith(f't {tick} '))
        if batch:s.type(batch,.25)
    problems=[];screen=ctx.screen_text(bin,s.out)
    if 'The sixth book is lit' not in screen or '3 + 3 + 3 = 9 / 9' not in screen:problems.append('three played tutorials did not reach the end card')
    s.type(b'b',.2)
    if 'VI. The fugue  [3*]' not in ctx.screen_text(bin,s.out):problems.append('sixth title book did not light')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    if not state.exists() or state.read_text().split()[-1]!='3':problems.append('sixth-book completion did not persist')
    return s,problems

ROWS['fugue-exposition-record']=fugue_record
ROWS['fugue-two-desks-record']=lambda bin,ctx:fugue_record(bin,ctx,3)
ROWS['fugue-end-card']=fugue_end


def fugue_junk_screen(bin, ctx, width=120, tier='rich'):
    """The terminal owns stderr too; compare every glyph and style after repaint."""
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
    s=ctx.Session([sys.executable,'-I',str(wrapper),str(width),str(height),bin,'--book','6','--no-title','--size',f'{width}x{height}','--tier',tier],height,width,env)
    s.pump(.5)
    events=[];problems=[]
    def compare(name,frames=2):
        cap=root/f'{name}.bin';cap.write_bytes(s.out)
        script=root/f'{name}.pk'
        script.write_text(f'pk 1\nseed 0\ntier {tier}\nsize {width}x{height}\nstart 22001\n'+''.join(f't 1 {key}\n' for key in events))
        got=subprocess.run([bin,'--apply',str(cap),'--size',f'{width}x{height}'],capture_output=True,text=True,timeout=30)
        expected=subprocess.run([bin,'--headless','--script',str(script),'--frames',str(frames),'--every',str(frames),'--dump',str(root/name),'--mute'],capture_output=True,text=True,timeout=30)
        if got.returncode or expected.returncode:
            problems.append(name+' terminal/headless command failed');return
        text,styles,_=got.stdout.split('--\n')
        want=(root/name/'final.txt').read_text();want_styles=(root/name/'final.sty').read_text()
        glyphs=sum(a!=b for a,b in zip(text,want))+abs(len(text)-len(want))
        good=glyphs==0 and styles==want_styles
        print(f'fugue junk {width}x{height} {tier} {name}: {width*height} cells, glyph differences {glyphs}, styles equal {styles==want_styles}')
        if not good:problems.append(f'{name}: terminal differs from complete headless frame ({glyphs} glyph cells, styles {styles==want_styles})')
        if tier=='rich':
            grain=sum(int(token.rsplit('*',1)[1]) for line in want_styles.splitlines() for token in line.split() if token.split(',')[1]=='223')
            print(f'fugue deliberate grain cells: {grain}')
    compare('first')
    for name,raw,keys in [('page-2',b'n',['new']),('page-3',b'n',['new']),('voice',b'v',['voice-switch']),('refusal',b'[[.',['split','split','dot'])]:
        s.type(raw,.65);events.extend(keys);compare(name)
    s.type(b'h',.4);s.pump(13.5);events.append('hear');compare('after-hear',400)
    s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
    return s,problems


def fugue_press_budget(bin, ctx, book=6):
    """Record read-to-carrying-frame latency, including Book VI h preparation."""
    import re,math
    root=Path(ctx.ROOT)/f'target/pty/fugue-press-budget-{book}';root.mkdir(parents=True,exist_ok=True)
    env=ctx.env_for();env['FUGUE_STATE']=str(root/'state');env['FUGUE_WAV_DIR']=str(root/'audio')
    s=ctx.Session([bin,'--book',str(book),'--no-title','--trace'],24,80,env)
    s.pump(.4);problems=[];rows=[]
    for name,raw in [('right',b'\x1b[C'),('right',b'\x1b[C'),('left',b'\x1b[D'),('up',b'\x1b[A'),('down',b'\x1b[B'),('hear',b'h')]:
        before=len(s.err);s.type(raw,.5)
        deadline=time.monotonic()+5
        while b'carries_key' not in s.err[before:] and time.monotonic()<deadline:s.pump(.05)
        found=re.findall(rb'trace frame (\d+) carries_key inner_us (\d+)',s.err[before:])
        if not found:problems.append('no carrying frame for '+name);continue
        tick,micros=map(int,found[-1]);frames=math.ceil(micros/(1000000/30))
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
    s=ctx.Session([bin,'--book','6','--no-title','--mute','--size',f'{width}x{height}'],height,width,env)
    s.type(b'nn',.3)
    keys={'up':b'\x1b[A','down':b'\x1b[B','right':b'\x1b[C','sharp':b'#','voice-switch':b'v'}
    source=(Path(ctx.ROOT)/f'tests/cases/book-6-preset-3-{width}.pk').read_text()
    s.type(b''.join(keys[x.split()[-1]] for x in source.splitlines() if x.startswith('t 1 ')),.5)
    s.type(b'v',.2)
    # Break the answer in bar 3, then inspect a different bar before returning.
    s.type(b'\x1b[C'*10+b'#'+b'\x1b[D'*10,.4)
    problems=[]
    def expect(label,bar,beat,pitch,figure=None):
        path=root/(label+'.bin');path.write_bytes(s.out)
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
    s.type(b'\x1b[C'*4,.25);expect('answer-second',2,1,'D5','exact-answer')
    s.type(b'\x1b[C'*6,.25);expect('answer-third',3,5,'Fb5','answer-transposition')
    s.type(b'v',.25);expect('counter-first',1,1,'A4','consonance')
    s.type(b'\x1b[C'*8,.25);expect('counter-second',2,1,'B4','consonance')
    s.type(b'\x1b[C'*12,.25);expect('counter-third',3,5,'D5')
    s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
    return s,problems

ROWS['fugue-cursor-panel-80']=lambda bin,ctx:fugue_cursor_panel(bin,ctx,80)
ROWS['fugue-cursor-panel-120']=lambda bin,ctx:fugue_cursor_panel(bin,ctx,120)


def fugue_cursor_motion(bin, ctx, cases=None):
    """Actual first-carrying-frame caret alignment, including held-note offsets."""
    import runpy,os,re,json
    Frames=runpy.run_path(str(Path(ctx.ROOT)/'tools/cursor-check.py'))['frame_session'](ctx)
    root=Path(ctx.ROOT)/'target/pty/fugue-cursor-motion';root.mkdir(parents=True,exist_ok=True)
    if cases is None:cases=[(desk,width,tier,mute) for desk in (0,1) for width in (80,120) for tier in ('rich','plain') for mute in (False,True)]
    problems=[];journal=[];last=None
    lengths=[4,4,8,4,4,4,2,2,8,8]
    for desk,width,tier,mute in cases:
        height=24 if width==80 else 40
        name=f'{desk}-{width}-{tier}-'+('mute' if mute else 'sound');path=root/(name+'.pk')
        env=ctx.env_for();env['FUGUE_STATE']=str(root/(name+'.state'));env['FUGUE_WAV_DIR']=str(root/(name+'-audio'))
        s=Frames([bin,'--book','6','--no-title','--size',f'{width}x{height}','--tier',tier,'--trace','--record',str(path)]+(['--mute'] if mute else []),height,width,env)
        last=s;s.pump(.2);s.type(b'nn',.5)
        if desk:s.type(b'v',.15)
        initial=s.out
        for key in (b'\x1b[C',b'\x1b[D'):s.type(key,.2)
        for key in (b'\x1b[C',b'\x1b[D'):
            begin=time.monotonic()
            for press in range(10):
                os.write(s.master,key);s.pump(max(.001,begin+(press+1)/30-time.monotonic()))
            s.pump(.2)
        s.type(b'q');s.finish(timeout=20);ctx.common_checks(s,0,problems)
        events=[(int(x.split()[1]),x.split()[2]) for x in path.read_text().splitlines() if x.startswith('t ') and x.split()[2] in ('left','right')]
        if [key for _,key in events]!=['right','left']+['right']*10+['left']*10:problems.append(name+' lost or reordered key')
        def image(data):
            cap=root/'frame.bin';cap.write_bytes(data)
            out=subprocess.run([bin,'--apply',str(cap),'--size',f'{width}x{height}'],capture_output=True,text=True,check=True)
            return out.stdout.split('--\n')[0].splitlines()
        def caret(screen):return [(y,x) for y,row in enumerate(screen) for x,ch in enumerate(row[:width-24]) if ch=='^']
        previous=caret(image(initial));position=0;records=[];unit=1 if desk else 2
        for tick,data in s.frames:
            keys=[(i,key) for i,(at,key) in enumerate(events) if at==tick-1]
            if not keys:continue
            for _,key in keys:position+=unit if key=='right' else -unit
            elapsed=0;x=9
            for length in lengths:
                if position<elapsed+length:break
                x+=max(6 if length==8 else 5 if length==4 else 4,(length+unit-1)//unit)
                elapsed+=length
                if elapsed%8==0:x+=1
            expected=x+(position-elapsed)//unit
            screen=image(data);current=caret(screen)
            panel=f'Bar {position//8+1}, beat {position%8+1}:8' in screen[5][width-22:]
            aligned=len(current)==1 and current[0][1]==expected
            moved=bool(current) and current!=previous
            for i,key in keys:records.append({'press':i+1,'key':key,'frame':tick,'panel_frames':1 if panel else None,'caret_frames':1 if aligned and moved else None,'caret':current,'expected_x':expected})
            if not panel or not aligned or not moved:problems.append(f'{name} press {keys[0][0]+1}: panel {panel}, caret {current}, expected x {expected}, moved {moved}')
            previous=current
        if len(records)!=22:problems.append(name+f' only {len(records)} accounted presses')
        journal.append({'case':name,'presses':records})
        print(f'fugue caret {name}: {sum(r["caret_frames"]==1 for r in records)}/22 aligned in first carrying frame')
    (root/'journal.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last,problems

ROWS['fugue-cursor-same-frame']=fugue_cursor_motion
