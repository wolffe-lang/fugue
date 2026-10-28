#!/usr/bin/env python3
"""Authored ordinary-key study cases, not presented as terminal recordings."""
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
rows=runpy.run_path(str(ROOT/'tests/cantus_rows.py'))
writing=rows['writing'];legal=rows['LEGAL'];solution=rows['solution'](ROOT)
for width,height in ((80,24),(120,40)):
    cases={
        'write': [],
        'legal': writing(legal)+['check'],
        'illegal': writing([28,28,29,30,31,30,29,28])+['check'],
        'pair': writing(legal)+['check','check'],
        'lower': writing(legal)+['voice-switch','check','check'],
        'solved': writing(legal)+['check','check']+solution+['check'],
    }
    for name,actions in cases.items():
        score=3 if name=='solved' else 0
        path=ROOT/f'tests/cases/book-7-{name}-{width}.pk'
        path.write_text(f'pk 1\nseed 0\ntier rich\nsize {width}x{height}\nstart 24001\n# frames 2 every 1\n# score {score}\n'+''.join(f't 1 {key}\n' for key in actions))
        print(path)
