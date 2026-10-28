from pathlib import Path
import runpy
import sys
import time

root=Path(sys.argv[1]);binary=sys.argv[2]
base=runpy.run_path(str(root/'.lair/tools/pty'))['Ctx']
rows=runpy.run_path(str(root/'tests/pty_rows.py'))
active=[]
class Early(base.Session):
    def __init__(self,*args):
        self.constructor=True
        super().__init__(*args)
        self.constructor=False
        active.append(self)
    def pump(self,seconds):
        if not getattr(self,'constructor',False):return super().pump(seconds)
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            super().pump(.001)
            if b'\x1b[?1049h' in self.out:return
class Ctx(base):Session=Early
try:
    s,problems=rows['fugue_right_then_up'](binary,Ctx)
    print('cold negotiation row problems:',problems,flush=True)
    sys.exit(bool(problems))
except Exception as e:
    print('cold negotiation row FAILED:',repr(e),flush=True)
    sys.exit(1)
finally:
    for s in active:
        if not hasattr(s,'status'):
            s.type(b'q',.1)
            s.finish()
