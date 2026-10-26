#!/usr/bin/env python3
"""Independent pitch spelling, clef geometry, interval and PCM fundamental proof."""
import argparse
import cmath
import math
from pathlib import Path
import struct
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--bin', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
out = root / 'target/pitch-proof'
subprocess.run([str((root / a.bin).resolve()), '--pitch-proof', str(out)], check=True)
rows = [line.split() for line in (out / 'pitches.txt').read_text().splitlines()[1:]]
assert {(int(r[0]), int(r[1])) for r in rows} == {(b, p) for b in range(1, 6) for p in range(6)}
notes = {}
census = {}
for r in rows:
    book, page, voice, event, pos, accidental = map(int, r[:6])
    name, clef, base, row, interval, low, high = r[6:]
    clef, base, row, low, high = map(int, [clef, base, row, low, high])
    expected_name = 'CDEFGAB'[pos % 7] + ('#' if accidental == 1 else '') + str(pos // 7)
    assert name == expected_name
    assert row == 34 - (pos - base)
    assert clef == (30 if low >= 25 else 18)
    notes[name] = 440 * 2 ** (((pos // 7)*12 + [0,2,4,5,7,9,11][pos % 7] + accidental - 57)/12)
    census[book, page] = (clef, max(0, (clef-low)//2), max(0, (high-clef-8)//2))

def fft(a):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j: a[i], a[j] = a[j], a[i]
    size = 2
    while size <= n:
        step = cmath.exp(-2j*math.pi/size)
        for start in range(0, n, size):
            w = 1
            for k in range(size//2):
                u, v = a[start+k], a[start+k+size//2]*w
                a[start+k], a[start+k+size//2] = u+v, u-v
                w *= step
        size *= 2
    return a

for name, expected in sorted(notes.items()):
    data = (out / (name+'.pcm')).read_bytes()
    samples = struct.unpack('<'+str(len(data)//2)+'h', data)[::2]
    # A 0.2-second stable segment avoids onset noise; zero padding permits
    # peak interpolation, without using the expected pitch to choose a bin.
    samples = samples[2400:12000]
    signal = [x*(.5-.5*math.cos(2*math.pi*i/(len(samples)-1))) for i,x in enumerate(samples)]
    spectrum = fft([complex(x) for x in signal] + [0j]*(65536-len(signal)))
    power = [abs(x) for x in spectrum[:4096]]
    peaks = [k for k in range(20, len(power)-1) if power[k]>power[k-1] and power[k]>power[k+1]]
    strongest = max(power[k] for k in peaks)
    k = next(k for k in peaks if power[k] > strongest*.02)
    # Group vibrato/window sidebands before selecting the fundamental peak.
    k = max((j for j in peaks if k <= j <= k + int(30*65536/48000)), key=lambda j: power[j])
    alpha, beta, gamma = [math.log(max(power[j], 1e-30)) for j in (k-1,k,k+1)]
    offset = .5*(alpha-gamma)/(alpha-2*beta+gamma)
    measured = (k+offset)*48000/65536
    error = abs(measured/expected-1)
    assert error < .01, (name, expected, measured, error)
    print(f'pitch-check: {name} expected={expected:.3f} fundamental={measured:.3f} error={error:.5%}')
print(f'pitch-check: {len(rows)} note rows, {len(notes)} distinct PCM fundamentals, 30 pages')
for (book,page), (clef,below,above) in sorted(census.items()):
    print(f'clef-census: book={book} page={page} clef={clef} ledgers-below={below} above={above}')
