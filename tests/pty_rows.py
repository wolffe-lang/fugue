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
