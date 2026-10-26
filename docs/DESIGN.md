# Design

Fugue is a counterpoint puzzle, not a transcription exercise. Book I gives a
cantus and asks for one note against every note. A legal answer passes; five
visible style measures award one to three stars. The first three pages share
one original contour in Ionian, Dorian and Mixolydian, making the raised cadence
audible without introducing a new melodic shape at the same time. Later pages
come from the seed, with the cantus alternately below and above.

## Boundaries

- `theory`: spelled pitches, six modes, intervals, motion, named melodic checks,
  pruned enumeration and shape ranking.
- `first`: the vertical judge, style measures and a bounded offline search that
  certifies a generated exercise has a legal solution. Its answer is discarded.
- `session`: notes, cursor, undo history, title/staff/card and playback position.
- `staff`: manuscript cells, palette, glyphs, title initial and critic.
- `ear`: prepared note WAVs and one two-voice part; output ownership.
- `fugue`: command-line options, live/headless adapters, recording and verification.

The pinned lair engine supplies terminal restoration, input decoding, the
30 Hz clock, grid/diff, noise, replay format and synthesis. No engine source is
changed by this game. The game and its tests compile as one wolf package with
symlinks into the staged engine, following the engine's documented package seam.

## Determinism

A seed, starting page, tier, size and tick-stamped keys determine every score
and frame. `--daily` selects the number of UTC days since the Unix epoch once,
before play; no musical rule reads a clock. Fifty seeds per mode exercise both
the raw melodic pool and the playable, solution-certified generator. All current
lines have ten notes, within the validator's eight-to-sixteen-note envelope.
A seed may share a line with another seed. A higher level is not necessarily a
harder one, and three stars are not promised for every seeded exercise.

The score's first legal solution is not used to judge another answer. Every
answer goes through the same named hard checks and separately measured style
rules. Generated exercises cycle through the best sixteen melodic candidates
from the seed's starting index until the offline search proves one legal on the
assigned side. Failure is not turned into a silently easier rule set.

## The live boundary

The layout has a fixed requested size, default 80x24; `--size 120x40` gives more
room to the page and critic. Resizing the terminal does not change the exercise
or remap its notes. A smaller initial window is refused by name. The staff keeps
one cell row per diatonic step; a range too large for the viewport gets ^/v
markers, and the selected note remains visible. C4 is bold when in view.

Listening takes one second per whole note. Edits and page changes wait until
the listening pass ends, so the highlighted notes continue to describe the WAV
being played. Quit always works. Terminal restoration happens before waiting
for any remaining audio release tail. The engine's decoder currently ignores
CSI-u keys; legacy Enter and arrow sequences work. Enhanced keyboard decoding
is an engine follow-on, not implemented privately here.
