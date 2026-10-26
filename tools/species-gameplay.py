#!/usr/bin/env python3
"""Black-box species gates on each compiled backend; scores are recomputed."""
from pathlib import Path
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--bin', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
binary = str((root / args.bin).resolve())
out = root / 'target/species-gameplay'
out.mkdir(parents=True, exist_ok=True)

def run(argv, expected=0):
    result = subprocess.run([binary, *argv], cwd=root, text=True, capture_output=True, timeout=240)
    print(result.stdout, end='')
    print(result.stderr, end='')
    assert result.returncode == expected, (argv, result.returncode, result.stderr)
    return result

verdicts = run(["--species-verdicts"])
assert verdicts.stdout == (root / 'tests/goldens/verdicts/species.txt').read_text()
assert len(verdicts.stdout.splitlines()) == 127
run(["--rhythm-audio-study"])

for book in range(2, 6):
    census = run(['--species-census', '--book', str(book)])
    assert f'book {book} legal 12/12' in census.stdout
    for preset in range(1, 4):
        source = root / f'tests/cases/book-{book}-preset-{preset}-80.pk'
        result = run(['--headless', '--script', str(source), '--frames', '321', '--every', '321',
                      '--from', '320', '--dump', str(out / f'{book}-{preset}'), '--mute'])
        assert 'verified score 3' in result.stderr
        final = (out / f'{book}-{preset}/final.txt').read_text()
        assert 'Legal    3 / 3 stars' in final
    source = root / f'tests/cases/book-{book}-preset-1-80.pk'
    tampered = out / f'book-{book}-tampered.pk'
    tampered.write_text(source.read_text().replace('# score 3', '# score 2'))
    result = run(['--headless', '--script', str(tampered), '--frames', '321', '--every', '321',
                  '--dump', str(out / f'tampered-{book}'), '--mute'], 1)
    assert 'UNVERIFIED score 3, claimed 2' in result.stderr
    recording = root / f'tests/replays/book-{book}-solved.pk'
    assert recording.exists(), f'missing actual pty recording: {recording}'
    last = max(int(line.split()[1]) for line in recording.read_text().splitlines() if line.startswith('t '))
    result = run(['--headless', '--script', str(recording), '--frames', str(last + 1),
                  '--every', str(last + 1), '--dump', str(out / f'recorded-{book}'), '--mute'])
    assert 'verified score 3' in result.stderr

run(['--book', '0'], 2)
run(['--book', '7'], 2)
print('species-gameplay: 48 certified seeds, 12 three-star references, four score refusals and four actual recordings green')
