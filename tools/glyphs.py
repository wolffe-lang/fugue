#!/usr/bin/env python3
"""Hold the documented non-ASCII glyph inventory to rendered evidence, both ways."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
want={int(x,16) for x in re.findall(r'U\+([0-9A-F]{4,6})',(root/'docs/GLYPHS.md').read_text())}
got=set()
for path in (root/'tests/goldens').rglob('*.txt'):
    chars={ord(c) for c in path.read_text() if ord(c)>127}
    if 'plain' in str(path):assert not chars, str(path)
    else:got |= chars
assert got == want, f'missing={want-got}, undocumented={got-want}'
print(f'glyphs: {len(got)} non-ASCII code points, both-way inventory green; plain is ASCII')
