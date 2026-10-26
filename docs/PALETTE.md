# Palette

| Role | Rich xterm index | Plain console index |
|---|---:|---:|
| Parchment | 230, sparse 223 grain variation | 7 |
| Grain / dim staff | 180 | 3 grain, 8 staff |
| Cantus | 130 (saturated burnt orange) | 1 (red) |
| Pitch names / critic labels | 94 | 3 |
| Counterpoint and headings | 24 | 4 |
| Perfect consonance | 22 | 2 |
| Imperfect consonance | 130 | 3 |
| Dissonance | 124 | 1 |
| Sounding note background | 222 | 11 |
| Current bar background | 223 | 15 |

The colours are roles, not verdicts on their own. P/i/x and interval numbers
keep the plain harmony row legible without colour, and the critic names every
hard break. `test_dissonance_is_never_drawn_green` holds the palette boundary;
style goldens hold the actual rendered indices. The two tiers have identical
geometry. Terminal theme choices can alter the sixteen-colour palette, so the
plain tier does not claim an exact RGB parchment colour.

`tools/staff-check.py` computes relative-luminance contrast for inks 130 and 24
against ground indices 230, 223 and 222, requiring at least 3:1 for these glyphs.
The cantus and player retain hollow and filled heads respectively; no halo is used.

Measured rich contrasts (relative luminance): burnt orange 130 is 4.605:1 on
230, 3.496:1 on 223, and 3.436:1 on 222. Dark blue 24 is respectively 6.876:1,
5.220:1 and 5.130:1. These are the checked cube values, not photographs of a
particular terminal theme or a claim that colour alone conveys voice identity.
