#!/usr/bin/env python3
"""Independent shape, style, playback and PCM checks on freshly rendered frames."""
import argparse
import hashlib
import math
from pathlib import Path
import struct
import subprocess

p = argparse.ArgumentParser(); p.add_argument('--bin', required=True); a = p.parse_args()
root = Path(__file__).resolve().parents[1]
binary = str((root / a.bin).resolve())

def styles(path):
    result = []
    for line in path.read_text().splitlines():
        row = []
        for run in line.split():
            cell, count = run.split('*')
            row.extend([tuple(map(int, cell.split(',')))] * int(count))
        result.append(row)
    return result

for cols, rows in [(80, 24), (120, 40)]:
    margin = cols - (29 if cols >= 100 else 24)
    width = (margin - 9) // 10
    bars = [7 + i * width for i in range(10)] + [margin - 2]
    for tier, line, bar, cf, cp in [('rich', '─', '│', '○', '●'), ('plain', '-', '|', 'o', '*')]:
        for case in ['walk', 'hear']:
            out = root / f'target/staff-check/{case}-{cols}-{tier}'
            subprocess.run([binary, '--headless', '--script', f'tests/cases/{case}-{cols}.pk', '--frames', '40' if case == 'walk' else '301', '--every', '1' if case == 'walk' else '30', '--tier', tier, '--dump', str(out)], cwd=root, check=True)
            for path in sorted(out.glob('frame-*.txt')):
                image = path.read_text().splitlines(); sty = styles(path.with_suffix('.sty'))
                # Every boundary crosses all five lines and four intervening spaces.
                ys = [y for y in range(rows) if image[y][7] == bar]
                assert len(ys) == 9 and ys == list(range(ys[0], ys[0]+9)), path
                for y in ys:
                    for x in bars: assert image[y][x] == bar, (path, y, x)
                for y in ys[::2]:
                    assert all(ch in {line, bar, cf, cp, '#'} for ch in image[y][7:margin-1]), (path, y)
                assert all('_' not in row for row in image), path
                assert 'h hear   Space sound   Enter check' in image[-2], path
                assert 'Editing bar 1' in image[4][margin+2:], path
                assert sty[4][margin+2][2] == 1, path
                if case == 'hear':
                    tick = int(path.stem.split('-')[1])
                    lit = [(y,x) for y,row in enumerate(image) for x,ch in enumerate(row) if ch in {cf,cp} and sty[y][x][1] == (222 if tier == 'rich' else 11)]
                    if tick < 300:
                        x = 8 + tick//30 * width
                        assert sorted(xx for _,xx in lit) == [x,x+1], (path,lit)
                    else: assert not lit, (path,lit)
        print(f'staff-check: {cols}x{rows} {tier}: forty walk frames, eleven listening frames green')

# W3C relative luminance, on the actual xterm cube, not a theme-dependent guess.
def rgb(index):
    levels = [0, 95, 135, 175, 215, 255]
    n = index - 16
    return [levels[n//36], levels[n//6%6], levels[n%6]]
def luminance(index):
    v = [c/255 for c in rgb(index)]
    linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in v]
    return sum(x*w for x,w in zip(linear, [.2126,.7152,.0722]))
for ink in [52,24]:
    for ground in [230,223,222]:
        contrast = (luminance(ground)+.05)/(luminance(ink)+.05)
        assert contrast >= (7 if ink == 52 else 3), (ink,ground,contrast)
        print(f'staff-check: palette {ink} on {ground} contrast {contrast:.3f}:1')

pcm_path = root/'target/staff-check/whole-seed7.pcm'
subprocess.run([binary,'--seed','7','--sound-replay',str(pcm_path)],cwd=root,check=True)
pcm = pcm_path.read_bytes()
assert len(pcm) == 10*192000
assert hashlib.sha256(pcm).hexdigest() == (root/'tests/goldens/audio/whole-seed7.sha256').read_text().strip()
# Energy in every bar and both stereo channels, with no clipping.
for bar in range(10):
    samples = struct.unpack('<96000h',pcm[bar*192000:(bar+1)*192000])
    rms = [math.sqrt(sum(x*x for x in samples[ch::2])/48000) for ch in range(2)]
    assert min(rms) > 50 and max(rms)/min(rms) < 2
    assert max(map(abs,samples)) < 32767
    print(f'staff-check: audio bar {bar+1} RMS L/R {rms[0]:.1f}/{rms[1]:.1f}')
print('staff-check: exact ten-second PCM golden green')
