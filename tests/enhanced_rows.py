"""Negotiated kitty-protocol rows; injected bytes, not a physical Ghostty capture."""
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import time

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
    class Kitty(ctx.Session):
        def __init__(self,*args):
            self.answered=False
            super().__init__(*args)
        def pump(self, seconds):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                super().pump(min(.002,end-time.monotonic()))
                if not self.answered and QUERY in self.out:
                    os.write(self.master,b'\x1b[?0u')
                    self.answered=True
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
                s=Kitty([binary,'--book',str(book),'--no-title','--mute','--trace','--record',str(record),'--size',f'{width}x{height}','--tier',tier],height,width,env)
                last=s
                if not s.answered or PUSH not in s.out:raise AssertionError('enhanced row did not negotiate flags 11')
                start=1 if book==1 else 10000+book*2000+1
                actions=[]
                def want():
                    script=root/'expected.pk';dest=root/'expected'
                    script.write_text(f'pk 1\nseed 7\ntier {tier}\nsize {width}x{height}\nstart {start}\n'+''.join(f't 1 {key}\n' for key in actions))
                    subprocess.run([binary,'--headless','--script',str(script),'--frames','2','--every','2','--dump',str(dest)],check=True,capture_output=True,timeout=30)
                    return (dest/'final.txt').read_text(),(dest/'final.sty').read_text()
                def inspect(capture):
                    return cantus['applied'](binary,root,capture,width,height)
                def send(key,kind=1):
                    before=len(s.err)
                    os.write(s.master,wire(key,kind))
                    if kind!=3:actions.append(key)
                    if kind!=3:
                        deadline=time.monotonic()+5
                        while b'carries_key' not in s.err[before:] and time.monotonic()<deadline:s.pump(.002)
                        trace=s.err[before:]
                        carrying=re.search(rb'trace frame (\d+) carries_key',trace)
                        if carrying is None:raise AssertionError('no completed carrying frame for '+key)
                        tick=int(carrying[1])
                        boundary=re.search(rb'trace output frame '+str(tick).encode()+rb' bytes (\d+)',trace)
                        if boundary is None:raise AssertionError('missing output boundary for carrying frame')
                        offset=int(boundary[1])
                        entry=s.out.index(b'\x1b[1;1H')
                        deadline=time.monotonic()+5
                        while len(s.out)<entry+offset and time.monotonic()<deadline:s.pump(.002)
                        actual=inspect(s.out[:entry+offset])
                        if actual!=want():
                            (root/'mismatch.bin').write_bytes(s.out[:entry+offset])
                            (root/'mismatch-trace.err').write_bytes(s.err)
                            s.type(wire('quit'));s.finish()
                            raise AssertionError(f'book {book} {width} {tier}: {key} kind {kind} has wrong first carrying-frame state')
                        journal.append(dict(book=book,size=f'{width}x{height}',tier=tier,key=key,kind=kind,frame=tick,bytes=wire(key,kind).hex(),exact=True))
                    else:
                        s.pump(.04)
                        if inspect(s.out)!=want():raise AssertionError('release changed the editor: '+key)
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
                text=record.read_text()
                got=[line.split()[-1] for line in text.splitlines() if line.startswith('t ')]
                if got!=actions+['quit']:problems.append('enhanced row lost, doubled or acted on a release')
                (root/'capture.bin').write_bytes(s.out);(root/'trace.err').write_bytes(s.err)
                print(f'enhanced keys book {book} {width} {tier}: flags11, eight repeat events each way, all controls, releases inert, restored')
    (Path(ctx.ROOT)/'target/pty/enhanced-keys.json').write_text(json.dumps(journal,indent=2)+'\n')
    return last,problems

ROWS={'enhanced-keys':enhanced_keys}
