from pathlib import Path
import runpy
import shutil
import sys
import time

root=Path(sys.argv[1]);binary=sys.argv[2];label=sys.argv[3]
ctx=runpy.run_path(str(root/'.lair/tools/pty'))['Ctx']
r=runpy.run_path(str(root/'tests/ear_rows.py'))
original=r['children']
def slow_children(s):
    time.sleep(.09)
    return original(s)
r['storm'].__globals__['children']=slow_children
s,problems=r['storm'](binary,ctx)
shutil.copytree(root/'target/pty/audition-storm',root.parent/label,dirs_exist_ok=True)
print('delayed owner observer problems:',problems,flush=True)
sys.exit(bool(problems))
