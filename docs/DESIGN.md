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


## Staff drawing seam

The staff helpers are pure over a supplied grid: no session mutation, clock,
terminal writes or sound preparation. Rhythm drawing can use them without
reimplementing geometry:

- `viewport(top, bottom, base, left, right) -> Viewport`: base is the diatonic
  position at the bottom; at least ten row steps are required. The lower line
  is `base + 2`. Supply in-grid rows and columns with space for margin names.
- `row_of(view, pitch) -> int` and `pitch_of(view, row) -> Pitch` are inverses
  for natural pitches; accidentals retain the letter's row. Rows outside the
  viewport remain mathematical rows, not clamped positions.
- `lines(mut grid, view, tier)` draws five uninterrupted horizontal runs.
- `draw_staff(mut grid, view, tier, bars)` adds the margin names and vertical
  crossings at supplied bar columns. Lay down grain/current-bar shading first.
- `ledger(mut grid, view, pitch, column, tier, cantus) -> int` adds three-cell
  ledgers or an edge ^/v, returning the unclamped row. It preserves existing
  bar crossings and heads.
- `head(mut grid, view, pitch, column, tier, cantus, selected, lit) -> int`
  calls the ledger helper and draws the hollow cantus or filled player head.
  It returns that same row for stems and ties. Supply a head column inside a
  bar with one cell of room on either side; this function never owns rhythm.
  A cadence sharp uses the free adjacent cell, not a cantus head or boundary.

Draw bar backgrounds and names before heads, then attach rhythm marks. Book I
uses two adjacent head columns, so unisons remain distinct. The editor and the
playback cursor are separate: playback shades its bar while the right panel's
first line continues to identify the selected edit location.

Playback rhythm has three named seams: `session.ticks_per_whole()` is the
single duration constant; `session.piece_ticks(state)` gives the phrase span;
`session.event_at(state, elapsed_ticks)` finds the lit event. Book I divides by
the whole-note span; rhythm can replace that lookup with beat lengths without
changing the staff or player owner. `ear.part(cantus, voice)` produces score
text from the event lists (currently pitches, all wholes); `whole_part(state)`
is only its adapter. Tempo and PCM duration derive from the same session clock.
## The rhythmic books

`rhythm` stores integer eighth-note lengths, rests and incoming ties. `species`
classifies figures, judges the sounding beats, and performs bounded solution
search separately from the player's answer. `presets` holds twelve fixed,
original tutorial pages and their test references; a reference is never copied
into the editor. `manuscript` maps musical time to widened columns and emits
rhythmic part text. `notation` composes the later pages on `staff`'s shared
viewport, pitch/row, ledger and head API. It does not draw a second kind of staff.

The seed selects a starting index in the same modal cantus pool. Candidates
are admitted only after the species checker verifies a bounded search result
on the requested side. Search tries sparse shapes and planned unique climaxes;
these are search preferences, not extra laws imposed on another answer. Budget
exhaustion is a named generation failure, never an assertion or a relaxed judge.
Florid starting grids mix wholes, halves, quarters and ties; eighths remain an
optional subdivision rather than an obligation imposed on every exercise.

The cursor advances in the book's smallest unit, even inside a held event.
Pitch changes follow its tie chain. A history entry retains the complete small
note/value lists, so undo restores duration, rests, ties and cursor offset as
well as pitch. The final bar remains a whole. Playback uses the same lengths as
the staff and score text, while the output owner remains in `ear`.

`progress` validates a tiny versioned file containing only five best-star
counts. It cannot supply music or bypass the judge. Recordings snapshot those
cosmetic title counts in an optional comment; the event stream still determines
all notes, rhythm, verdicts and final stars.
