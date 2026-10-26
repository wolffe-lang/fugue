#!/usr/bin/env python3
"""Author ordinary-key Book VI scripts from explicit original reference spellings.
Run on the Linux lane; these are authored scripts, not terminal recordings.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
# Subject, exact answer, and octave-invertible continuation, in spelled pitch space.
SUBJECTS = [[28,30,31,32,31,30,28,30,29,28],
            [30,34,33,34,35,37,36,34,35,34],
            [35,33,32,33,34,36,35,33,34,35]]
ANSWERS = [[32,34,35,36,35,34,32,34,33,32],
           [34,38,37,38,39,41,40,38,39,38],
           [38,37,36,37,38,40,39,37,38,39]]
COUNTERS = [[30,29,30,31,33,29,30,29,28,32],
            [34,33,32,33,37,36,35,36,34,36],
            [33,32,34,35,36,35,34,35,33,32]]
VALUES = [[4,2,2,4,4,8,4,4,8,8], [4,4,8,4,4,4,2,2,8,8], [4,4,8,4,4,4,2,2,8,8]]

def edits(initial, wanted, sharps, values, unit=1):
    keys = []
    for i, (a,b) in enumerate(zip(initial,wanted)):
        keys += ['up' if b > a else 'down'] * abs(b-a)
        if i in sharps: keys.append('sharp')
        if i + 1 < len(initial): keys += ['right'] * (values[i]//unit)
    return keys

def solve(index):
    out = []
    if index != 1:
        out += edits(SUBJECTS[index], ANSWERS[index], [4,8] if index == 2 else [], VALUES[index], unit=2)
    if index == 2: out += ['voice-switch']
    if index != 0:
        out += edits([30 if index == 1 else 31]*10, COUNTERS[index], [], VALUES[index])
    return out

def write(name, width, start, events, frames, every, score, seed=0):
    text = f'pk 1\nseed {seed}\ntier rich\nsize {width}x{24 if width == 80 else 40}\nstart {start}\n# score {score}\n# frames {frames} every {every}\n'
    text += ''.join(f't {tick} {key}\n' for tick,key in events)
    (ROOT/'tests/cases'/f'{name}-{width}.pk').write_text(text)

for width in (80,120):
    for i in range(3):
        events = [(1,k) for k in solve(i)] + [(2,'hear'),(365,'check')]
        write(f'book-6-preset-{i+1}',width,22001+i,events,366,60,3)
    write('book-6-hear',width,22001,[(1,k) for k in solve(0)]+[(2,'hear')],362,30,3)
    write('book-6-wrong',width,22001,[(1,k) for k in solve(0)]+[(2,'up'),(3,'check')],4,1,0)
    write('book-6-seed',width,22000,[(1,'hear')],362,90,0,seed=7)
    events=[]
    for i in range(3):
        events += [(1+i*3,k) for k in solve(i)] + [(2+i*3,'check')]
        if i < 2: events.append((3+i*3,'new'))
    write('book-6-end',width,22001,events,10,1,3)
    write('book-6-complete',width,22001,events+[(9,'desk')],11,10,3)
print('fugue fixtures: sixteen authored cases, not recordings')
