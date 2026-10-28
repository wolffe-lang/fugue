"""Own-cantus real-input, complete-frame and historical-oracle witnesses."""
import json
import re
from pathlib import Path
import subprocess
import time

KEYS = {'up':b'\x1b[A','down':b'\x1b[B','left':b'\x1b[D','right':b'\x1b[C',
        'check':b'\r','undo':b'u','split':b'[','join':b']','mode':b'm',
        'voice-switch':b'v','retry':b'r','quit':b'q','desk':b'b','hear':b'h',
        'sound':b' ','sharp':b'#'}
LEGAL = [28,29,30,28,31,30,32,30,29,28]
MODES = ['Ionian','Dorian','Phrygian','Lydian','Mixolydian','Aeolian']
FUX = {
    'Dorian': [(3,'sequence'),(5,'sequence'),(7,'sequence'),(8,'sequence'),(1,'balance')],
    'Phrygian': [(3,'sequence')],
    'Lydian': [(5,'successive-leaps'),(9,'recovery'),(10,'successive-leaps'),(1,'leap-count')],
    'Mixolydian': [(6,'recovery'),(6,'successive-leaps'),(9,'recovery'),(9,'sequence'),(10,'successive-leaps'),(1,'leap-count')],
    'Aeolian': [(1,'sequence'),(2,'sequence'),(3,'sequence'),(7,'sequence'),(7,'sequence'),(8,'sequence'),(9,'sequence')],
    'Ionian': [(9,'sequence')],
}

def writing(positions, mode=0):
    actions = ['mode']*mode
    initial = [28]*10
    while len(initial)<len(positions):
        actions.append('split'); initial.append(28+mode)
    while len(initial)>len(positions):
        actions.append('join'); initial.pop(0)
    for i,pos in enumerate(positions):
        delta=pos-initial[i]
        actions.extend(['up' if delta>0 else 'down']*abs(delta))
        if i+1<len(positions): actions.append('right')
    return actions


def solution(root):
    return [line.split()[-1] for line in (root/'tests/cases/preset-1-80.pk').read_text().splitlines()
            if line.startswith('t ') and line.split()[-1] not in ('hear','check','quit')]


def applied(binary, root, capture, width, height):
    path=root/'screen.bin';path.write_bytes(capture)
    result=subprocess.run([binary,'--apply',str(path),'--size',f'{width}x{height}'],capture_output=True,check=True,timeout=30)
    text,styles,_=result.stdout.decode().split('--\n')
    return text,styles


def expected(binary, root, actions, width, height, tier):
    path=root/'expected.pk'
    path.write_text(f'pk 1\nseed 0\ntier {tier}\nsize {width}x{height}\nstart 24001\n'+''.join(f't 1 {key}\n' for key in actions))
    dest=root/'expected'
    subprocess.run([binary,'--headless','--script',str(path),'--frames','2','--every','2','--dump',str(dest)],check=True,capture_output=True,timeout=30)
    return (dest/'final.txt').read_text(),(dest/'final.sty').read_text()


def expect(binary, root, s, actions, width, height, tier):
    want=expected(binary,root,actions,width,height,tier)
    deadline=time.monotonic()+5
    while True:
        got=applied(binary,root,s.out,width,height)
        if got==want:return got[0]
        if time.monotonic()>=deadline:raise AssertionError('own-cantus full glyph/style state differs')
        s.pump(.02)


def whole_session(binary, ctx):
    problems=[];last=None;journal=[]
    for width,height in ((80,24),(120,40)):
        for tier in ('rich','plain'):
            root=Path(ctx.ROOT)/f'target/pty/cantus-session-{width}-{tier}'
            root.mkdir(parents=True,exist_ok=True)
            state=root/'state';state.write_text('fugue 2 1 2 3 1 2 3\n')
            record=root/'session.pk'
            env=ctx.env_for();env['FUGUE_STATE']=str(state)
            s=ctx.Session([binary,'--book','7','--no-title','--mute','--size',f'{width}x{height}','--tier',tier,'--record',str(record)],height,width,env)
            last=s;actions=[]
            def send(keys):
                actions.extend(keys);s.type(b''.join(KEYS[key] for key in keys),.1)
                return expect(binary,root,s,actions,width,height,tier)
            send(writing(LEGAL))
            card=send(['check'])
            if not all(text in card for text in ('A legal cantus','Shape 106 = 100 - 6 + 4 x 3','Ascent 4, descent 5','Interval sizes 3')):
                problems.append('legal cantus shape measures absent or incorrect')
            if state.read_text()!='fugue 2 1 2 3 1 2 3\n':problems.append('cantus checking prematurely awarded progress')
            send(['check'])
            # Full frame equality holds the accepted score pitches, staff and
            # first-species editor to the same keyed state, not a supplied answer.
            send(solution(Path(ctx.ROOT)))
            card=send(['check'])
            if 'Legal    3 / 3 stars' not in card:problems.append('own cantus exercise did not reach three stars')
            s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
            if state.read_text()!='fugue 3 1 2 3 1 2 3 3\n':problems.append('v2 migration or seventh progress count failed')
            text=record.read_text();ticks=max(int(line.split()[1]) for line in text.splitlines() if line.startswith('t '))+1
            result=subprocess.run([binary,'--headless','--script',str(record),'--frames',str(ticks),'--every',str(ticks),'--dump',str(root/'verify')],capture_output=True,text=True,timeout=30)
            if result.returncode or 'verified score 3' not in result.stderr:problems.append('whole-session recording did not verify: '+result.stderr)
            journal.append(dict(size=f'{width}x{height}',tier=tier,score=3,keys=len(actions),record=str(record)))
            print(f'own-cantus session {width} {tier}: write, legal shape, unchanged cantus, solve, card, v2->v3, verified replay')
    (Path(ctx.ROOT)/'target/pty/cantus-sessions.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last,problems


def fux_by_keys(binary, ctx, tier='rich'):
    problems=[];last=None
    source=Path(ctx.ROOT)/'tests/oracles/fux.txt'
    for line in source.read_text().splitlines():
        if not line or line.startswith('#'):continue
        mode,_,spelling=line.split('|')
        positions=[int(p[-1])*7+'CDEFGAB'.index(p[0]) for p in spelling.split()]
        root=Path(ctx.ROOT)/f'target/pty/cantus-fux-{mode}-{tier}'
        root.mkdir(parents=True,exist_ok=True)
        s=ctx.Session([binary,'--book','7','--no-title','--mute','--tier',tier],24,80,ctx.env_for());last=s
        actions=writing(positions,MODES.index(mode))+['check']
        s.type(b''.join(KEYS[key] for key in actions),.2)
        screen=expect(binary,root,s,actions,80,24,tier)
        actual=re.findall(r'Bar (\d+): ([a-z-]+) /',screen)
        actual=[(int(bar),rule) for bar,rule in actual]
        if actual!=FUX[mode]:problems.append(f'{mode}: keyed critic {actual}, oracle {FUX[mode]}')
        s.type(b'q');s.finish();ctx.common_checks(s,0,problems)
        (root/'capture.bin').write_bytes(s.out)
        print(f'own-cantus Fux {mode} {tier}: keyed critic {actual}; oracle {FUX[mode]}')
    return last,problems

def fux_both_tiers(binary,ctx):
    problems=[];last=None
    for tier in ('rich','plain'):
        last,errors=fux_by_keys(binary,ctx,tier)
        problems.extend(errors)
    return last,problems

ROWS={'own-cantus-session':whole_session,'own-cantus-fux-keys':fux_both_tiers}
