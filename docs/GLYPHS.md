# Glyphs

| Code point | Glyph | Purpose |
|---|---|---|
| U+00B7 | · | Faint parchment grain |
| U+2500 | ─ | Staff and ledger lines |
| U+2502 | │ | The critic's margin |
| U+25CB | ○ | Hollow cantus note |
| U+25CF | ● | Filled counterpoint note |
| U+2588 | █ | The illuminated initial |

Every other mark is ASCII. The plain tier uses dashes, bars, o, * and # at the
same coordinates, plus P/i/x for consonance classes. `tools/glyphs.py` compares
this inventory against every rendered golden in both directions; it also
requires plain goldens to be ASCII. Fonts with ambiguous-width circle marks
may need `--plain`. Actual Terminal.app, iTerm2, Linux VT and PAX font-width
measurements are not claimed by a pseudo-terminal test.
