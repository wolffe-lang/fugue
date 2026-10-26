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
    if len(bank) != 16: problems.append('two-octave bank plus raised seventh missing')
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
    if 'First break' not in screen[16][58:]:
        problems.append('first break is not distinguished from the editing cursor')
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
