#!/usr/bin/env python3
"""Compiled Book VI gates: independent expected census, editor scripts and PCM."""
from pathlib import Path
import argparse
import hashlib
import struct
import subprocess

p=argparse.ArgumentParser(); p.add_argument('--bin',required=True); args=p.parse_args()
root=Path(__file__).resolve().parents[1]; binary=str((root/args.bin).resolve())
out=root/'target/fugue-gameplay'; out.mkdir(parents=True,exist_ok=True)
def run(argv, status=0, timeout=180):
    print('fugue-gameplay:', ' '.join(argv), f'watchdog {timeout}s', flush=True)
    r=subprocess.run([binary,*argv],cwd=root,capture_output=True,text=True,timeout=timeout)
    print(r.stdout,end=''); print(r.stderr,end='')
    assert r.returncode==status,(argv,r.returncode,r.stderr)
    return r

run(['--fugue-audio-study'])
# This offline traversal grew from 1,955 to 13,085 positions (6.7x). Keep the
# same bounded watchdog allowance per position; frame/latency gates do not change.
run(['--fugue-cursor-census'], timeout=7*180)
census=run(['--fugue-census']).stdout
assert 'subjects 300/300 real 300/300 tonal 52/300 counter 174/300 three-star 21/300 certified-mode-sides 12/12' in census
verdicts=run(['--fugue-verdicts']).stdout
assert verdicts==(root/'tests/goldens/verdicts/fugue.txt').read_text()
for index in range(1,4):
    case=root/f'tests/cases/book-6-preset-{index}-80.pk'
    r=run(['--headless','--script',str(case),'--frames','366','--every','366','--dump',str(out/f'preset-{index}'),'--mute'])
    assert 'verified score 3' in r.stderr
    assert 'Legal exposition    3 / 3 stars' in (out/f'preset-{index}/final.txt').read_text()
    pcm=out/f'exposition-{index}.pcm'
    run(['--script',str(case),'--frames','366','--sound-replay',str(pcm),'--mute'])
    data=pcm.read_bytes(); assert len(data)==12*192000
    digest=hashlib.sha256(data).hexdigest()
    assert digest==(root/f'tests/goldens/audio/exposition-{index}.sha256').read_text().strip(),digest
    for bar in range(12):
        samples=struct.unpack('<'+'h'*(192000//2),data[bar*192000:(bar+1)*192000])
        assert any(samples),(index,bar,'silent bar')
        assert max(abs(x) for x in samples)<32767,(index,bar,'clipping')
    print(f'exposition PCM {index}: twelve nonzero unclipped bars sha256 {digest}')

case=root/'tests/cases/book-6-preset-1-80.pk'
tampered=out/'tampered.pk';tampered.write_text(case.read_text().replace('# score 3','# score 2'))
r=run(['--headless','--script',str(tampered),'--frames','366','--every','366','--dump',str(out/'tampered'),'--mute'],1)
assert 'UNVERIFIED score 3, claimed 2' in r.stderr
r=run(['--headless','--script',str(root/'tests/cases/book-6-end-80.pk'),'--frames','10','--every','10','--dump',str(out/'end'),'--mute'])
assert 'The sixth book is lit' in (out/'end/final.txt').read_text()
assert '3 + 3 + 3 = 9 / 9' in (out/'end/final.txt').read_text()
for name in ('book-6-solved.pk','book-6-two-desks.pk'):
    record=root/'tests/replays'/name
    assert record.exists(),f'missing actual Book VI terminal recording: {name}'
    last=max(int(x.split()[1]) for x in record.read_text().splitlines() if x.startswith('t '))
    r=run(['--headless','--script',str(record),'--frames',str(last+1),'--every',str(last+1),'--dump',str(out/name.removesuffix('.pk')),'--mute'])
    assert 'verified score 3' in r.stderr
run(['--book','7'],2)
print('fugue-gameplay: subjects, answers, inversion admission, three references, end card, actual recording and PCM green')
