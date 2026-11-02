"""Negotiated kitty-protocol rows; injected bytes, not a physical Ghostty capture.

Keys are typed through tests/paced.py (fg04, fugue#36). The stand-in
terminal answers the keyboard query while the session drains output, so the
answer never waits on a settle. The game negotiates within its own 150 ms
window; a session the host stalled past that window starts in legacy mode, is
out of its case and is driven again. Each press, repeat and release is
written once the game has drawn the last, acknowledged by the game's own
trace, and its frame is compared at the exact output boundary with the
headless state of the same keys at the same hearing tick.
"""
import json
import os
from pathlib import Path
import re
import runpy
import subprocess

PACED = runpy.run_path(str(Path(__file__).with_name('paced.py')))
QUERY=b'\x1b[?u'
PUSH=b'\x1b[>11u'
POP=b'\x1b[<u'

def wire(key, kind=1):
    arrows={'up':'A','down':'B','left':'D','right':'C','octave-up':'A','octave-down':'B'}
    mods=2 if key in ('octave-up','octave-down','sharp') else 1
    if key in arrows:return f'\x1b[1;{mods}:{kind}{arrows[key]}'.encode()
    codes={'check':13,'quit':113,'escape':27,'sound':32,'hear':104,'undo':117,'new':110,
           'retry':114,'desk':98,'split':91,'join':93,'dot':46,'tie':116,'rest':48,
           'sharp':51,'voice-switch':118,'mode':109}
    code=int(key[-1])+48 if key.startswith('book-') else codes[key]
    return f'\x1b[{code};{mods}:{kind}u'.encode()


def negotiated(ctx):
    Paced=PACED['session'](ctx)
    class Kitty(Paced):
        def __init__(self,argv,rows,cols,env):
            super().__init__(argv,rows,cols,env,0.0,[(QUERY,b'\x1b[?0u')])
        @property
        def answered(self):
            return not self.replies
    return Kitty


def enhanced_keys(binary,ctx):
    cantus=runpy.run_path(str(Path(__file__).with_name('cantus_rows.py')))
    Kitty=negotiated(ctx)
    problems=[];last=None;journal=[]
    for book in range(1,8):
        for width,height in ((80,24),(120,40)):
            for tier in ('rich','plain'):
                root=Path(ctx.ROOT)/f'target/pty/enhanced-{book}-{width}-{tier}'
                root.mkdir(parents=True,exist_ok=True)
                record=root/'record.pk'
                env=ctx.env_for();env['FUGUE_STATE']=str(root/'state')
                start=1 if book==1 else 10000+book*2000+1
                def session(n):
                    s=Kitty([binary,'--book',str(book),'--no-title','--mute','--trace','--record',str(record),'--size',f'{width}x{height}','--tier',tier],height,width,env)
                    s.ready()
                    if s.answered and s.negotiated():return s
                    # The game's window closed before it read the answer:
                    # this session runs legacy keys, which is not this case.
                    answered=s.answered
                    s.type(b'q');s.finish()
                    raise PACED['Unrealised']('flags 11 not negotiated (query answered %s)' % answered)
                s=PACED['redrive'](f'enhanced keys book {book} {width} {tier}',session,problems)
                if s is None:raise AssertionError('enhanced row did not negotiate flags 11')
                last=s
                actions=[];hearing=[];heard_live={'on':False}
                def want(frames=2):
                    script=root/'expected.pk';dest=root/'expected'
                    script.write_text(f'pk 1\nseed 7\ntier {tier}\nsize {width}x{height}\nstart {start}\n'+''.join(f't 1 {key}\n' for key in actions))
                    subprocess.run([binary,'--headless','--script',str(script),'--frames',str(frames),'--every',str(frames),'--dump',str(dest)],check=True,capture_output=True,timeout=30)
                    return (dest/'final.txt').read_text(),(dest/'final.sty').read_text()
                def inspect(capture):
                    return cantus['applied'](binary,root,capture,width,height)
                def send(key,kind=1):
                    if kind!=3:actions.append(key)
                    ack=s.send(wire(key,kind),carries=kind!=3)
                    capture=s.frame(ack['frame'])
                    if key=='hear' and kind==1:heard_live['on']=True
                    if heard_live['on']:
                        # The hearing's frames move with its ticks: compare these
                        # after the session, at the same hearing tick.
                        hearing.append((key,kind,ack,capture));return
                    if inspect(capture)!=want():
                        (root/'mismatch.bin').write_bytes(capture)
                        (root/'mismatch-trace.err').write_bytes(s.err)
                        s.type(wire('quit'));s.finish()
                        raise AssertionError(f'book {book} {width} {tier}: {key} kind {kind} has wrong first carrying-frame state')
                    journal.append(dict(book=book,size=f'{width}x{height}',tier=tier,key=key,kind=kind,frame=ack['frame'],bytes=wire(key,kind).hex(),exact=True))
                # One press, seven repeats, one release: exactly eight events,
                # then the same leftward. No timer manufactures extra actions.
                for key in ('right','left'):
                    send(key)
                    for _ in range(7):send(key,2)
                    send(key,3)
                for key in ('up','down','octave-up','octave-down','sharp','sound','hear'):
                    # Hearing would lock the editor for ten seconds; it is the
                    # final control below, after all ordinary editor controls.
                    if key=='hear':continue
                    send(key);send(key,3)
                for key in ('undo','split','join','dot','tie','rest','voice-switch','mode','check','retry','new','desk'):
                    send(key);send(key,3)
                for n in range(1,8):send('book-'+str(n))
                send('hear');send('hear',3)
                s.type(wire('quit'));s.finish();ctx.common_checks(s,0,problems)
                if POP not in s.out or s.out.rfind(POP)>s.out.rfind(b'\x1b[?1049l'):problems.append('keyboard stack did not pop before leave')
                keys=s.verify(record,f'enhanced-{book}-{width}-{tier}',problems)
                got=[k for _,k in keys]
                if got!=actions+['quit']:problems.append('enhanced row lost, doubled or acted on a release')
                # The hearing frames: the headless state with h applied on
                # tick 1 and the same number of hearing ticks as the live frame.
                heard=next((t for t,k in keys if k=='hear'),None)
                for key,kind,ack,capture in hearing:
                    if heard is None or inspect(capture)!=want(ack['frame']-heard+1):
                        (root/'mismatch.bin').write_bytes(capture)
                        problems.append(f'book {book} {width} {tier}: {key} kind {kind} has wrong carrying-frame state at hearing tick {None if heard is None else ack["frame"]-heard}')
                    else:
                        journal.append(dict(book=book,size=f'{width}x{height}',tier=tier,key=key,kind=kind,frame=ack['frame'],bytes=wire(key,kind).hex(),exact=True,hearing_tick=ack['frame']-heard))
                (root/'capture.bin').write_bytes(s.out);(root/'trace.err').write_bytes(s.err)
                print(f'enhanced keys book {book} {width} {tier}: flags11, eight repeat events each way, all controls, releases inert, restored')
    (Path(ctx.ROOT)/'target/pty/enhanced-keys.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last,problems

ROWS={'enhanced-keys':enhanced_keys}
