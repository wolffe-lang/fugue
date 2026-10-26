# Palette

| Role | Rich xterm index | Plain console index |
|---|---:|---:|
| Parchment | 230, sparse 223 grain variation | 7 |
| Grain / dim staff | 180 | 3 grain, 8 staff |
| Cantus and pitch names | 94 | 3 |
| Counterpoint and headings | 24 | 4 |
| Perfect consonance | 22 | 2 |
| Imperfect consonance | 130 | 3 |
| Dissonance | 124 | 1 |
| Sounding note background | 222 | 11 |

The colours are roles, not verdicts on their own. P/i/x and interval numbers
keep the plain harmony row legible without colour, and the critic names every
hard break. `test_dissonance_is_never_drawn_green` holds the palette boundary;
style goldens hold the actual rendered indices. The two tiers have identical
geometry. Terminal theme choices can alter the sixteen-colour palette, so the
plain tier does not claim an exact RGB parchment colour.
