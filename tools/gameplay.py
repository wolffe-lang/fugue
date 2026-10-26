#!/usr/bin/env python3
"""Black-box native/release witnesses; never trust a score comment as a verdict."""
from pathlib import Path
import argparse
import subprocess
p=argparse.ArgumentParser();p.add_argument('--bin',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
bin=str((root/a.bin).resolve())
def run(args,expected=0):
    p=subprocess.run([bin]+args,cwd=root,capture_output=True,text=True)
    print(p.stdout,end='');print(p.stderr,end='')
    if p.returncode!=expected:raise SystemExit(f'gameplay FAILED: {args}, exit {p.returncode}, expected {expected}')
    return p
p=run(['--verdicts'])
assert p.stdout == (root/'tests/goldens/verdicts/rules.txt').read_text()
run(['--game-census'])
for i in range(1,4):
    p=run(['--headless','--script',f'tests/cases/preset-{i}-80.pk','--frames','361','--every','361','--dump',f'target/gameplay/preset-{i}'])
    assert 'verified score 3' in p.stderr
root.joinpath('target/gameplay').mkdir(parents=True,exist_ok=True)
case=root/'target/gameplay/tampered.pk'
case.write_text((root/'tests/cases/preset-1-80.pk').read_text().replace('# score 3','# score 2'))
p=run(['--headless','--script',str(case),'--frames','361','--every','361','--dump','target/gameplay/tampered'],1)
assert 'UNVERIFIED score 3, claimed 2' in p.stderr
run(['--size','79x24'],2)
run(['--size','80x23'],2)
record=root/'tests/replays/solved-80.pk'
ticks=int([x.split()[1] for x in record.read_text().splitlines() if x.endswith(' quit')][-1])+1
p=run(['--headless','--script',str(record),'--frames',str(ticks),'--dump','target/gameplay/recorded'])
assert 'verified score 3' in p.stderr
print('gameplay: census, three references, score-tampering and minimum refusals green')
