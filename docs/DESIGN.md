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
one cell row per diatonic step; a range too large for the viewport gets !/v
markers, and the selected note remains visible. C4 is bold when in view.

Listening takes one second per whole note. Edits and page changes wait until
the listening pass ends, so the highlighted notes continue to describe the WAV
being played. Quit always works. Terminal restoration happens before waiting
for any remaining audio release tail. `term.open_input` negotiates kitty
flags 11 at the requested layout floor. Its buffered startup bytes are fed once
to `input.events_all`; press/repeat events are projected to one editor action,
and releases are ignored. Legacy bytes follow the same event path without a
negotiated keyboard stack. Close pops a negotiated stack before restoration.


## Staff drawing seam

The staff helpers are pure over a supplied grid: no session mutation, clock,
terminal writes or sound preparation. Rhythm drawing can use them without
reimplementing geometry:

- `viewport(top, bottom, base, left, right) -> Viewport`: base is the diatonic
  position at the bottom; at least ten row steps are required. It defaults to
  treble, whose lower line stays E4 (30), independent of base. Supply in-grid
  rows and columns with space for margin names.
- `row_of(view, pitch) -> int` and `pitch_of(view, row) -> Pitch` are inverses
  for natural pitches; accidentals retain the letter's row. Rows outside the
  viewport remain mathematical rows, not clamped positions.
- `lines(mut grid, view, tier)` draws five uninterrupted horizontal runs.
- `draw_staff(mut grid, view, tier, bars)` adds the margin names and vertical
  crossings at supplied bar columns. Lay down grain/current-bar shading first.
- `ledger(mut grid, view, pitch, column, tier, cantus) -> int` adds three-cell
  ledgers or an edge !/v, returning the unclamped row. It preserves existing
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
`session.event_at(state, elapsed_ticks)` finds the lit event through the rhythmic
grid, including Book I's wholes. `ear.part(cantus, voice)` remains the whole-note
adapter; `whole_part(state)` uses `manuscript.part` for later books' lengths,
rests and ties. Tempo and PCM duration derive from the same session clock.
Neither adapter changes the player owner.
## The rhythmic books

`rhythm` stores integer eighth-note lengths, rests and incoming ties. `species`
classifies figures, judges the sounding beats, and performs bounded solution
search separately from the player's answer. `presets` holds twelve fixed,
original tutorial pages and their test references; a reference is never copied
into the editor. `manuscript` maps written events to content-sized columns and emits
rhythmic part text. `notation` composes the later pages on `staff`'s shared
viewport, pitch/row, ledger and head API. It does not draw a second kind of staff.

The seed selects a starting index in the same modal cantus pool. Candidates
are admitted only after the species checker verifies a bounded search result
on the requested side. Search tries sparse shapes and planned unique climaxes;
these are search preferences, not extra laws imposed on another answer. Budget
exhaustion is a named generation failure, never an assertion or a relaxed judge.
Florid starting grids mix wholes, halves, quarters and ties; eighths remain an
optional subdivision rather than an obligation imposed on every exercise.

The cursor selects one notated event per Left/Right press in every book,
including rests and ties. Pitch changes follow its tie chain. A history entry
retains the complete small note/value lists and event index, so undo restores
duration, rests, ties, pitch and the selected event. There is no cursor offset.
The final bar remains a whole. Playback uses the same lengths as
the staff and score text, while the output owner remains in `ear`.

`progress` validates a tiny versioned file containing only seven best-star
counts. It cannot supply music or bypass the judge. Recordings snapshot those
cosmetic title counts in an optional comment; the event stream still determines
all notes, rhythm, verdicts and final stars.

## Page-owned notation and editing

`staff.with_clef(view, line)` selects fixed E4 (30) or G2 (18).
`staff.system(state, view)` configures the page's single or grand staff while
preserving `viewport`, `row_of`, `pitch_of`, `draw_staff`, `ledger` and `head`
signatures. `head` still returns its actual row; its existing cantus boolean
selects that voice's staff inside the system. Both staves share one pitch map.
`staff.label_row(view, highest_pitch)` supplies a row above a voice's stem for
entry labels. `staff.interval_row` supplies the first free row below a column's
lowest drawn element. `staff.accidental(tier, value)` supplies flat/natural/sharp
cells. No engine drawing or output-owner change is needed.

Session fields `clef`, `grand`, `cantus_clef` and `voice_clef` are chosen once
when the page opens. `range_low`/`range_high` are inclusive diatonic positions,
shared by the editor and prepared audition bank. A Book VI page can set C3–C7
(21–49) before preparation. `rhythm_editable` gates the florid keys: fixed
answer versus editable countersubject. Engraving density remains independent
of navigation: `manuscript.spacing_unit` privately preserves existing held-value
widths. There is no `session.editor_unit` or within-event cursor field.
Book VI's accidentals cycle freely; earlier books keep the guard.

Replay IDs 1–25 are unchanged, 26/27 reserved as `book-6`/`voice-switch` for
Book VI, and `dot` is appended at 28. The terminal brackets now match their
hint: `[` split and `]` join. The `retry` replay event is r; at an editable
staff it toggles a rest, while on the critic card it returns to editing.

The selected-event panel derives its bar and eighth-beat from cursor time,
its vertical interval from the two score pitches, and its figure from the
existing classifier. `species.event_breaks` runs the same vertical/motion rule pass as the judge
but retains only findings emitted at the selected event. The separately titled bar list filters the global verdict by the active bar,
including melodic findings at that bar. Each finding row names its bar.
The critic card after Enter retains the complete verdict and global counts.
In every book the caret uses the selected event's attack column; the panel's
bar and eighth-beat are that event's onset. Compact grand staves fall back to
the bar-number row rather than hiding the caret.


## Supplied panel status

`staff.panel_data(mut grid, data: staff.PanelData, margin, tier)` is the common
column renderer. It owns geometry, palette, named bar rows and filtering both
finding lists to the active bar. `staff.panel` retains the session adapter for
Books I–V; a page with another judge or moving voice supplies data directly.
No session state, judge callback, clock or audio owner is held by the renderer.

`PanelFinding` has one-based `bar: int` and `rule: str`. `PanelData` has one-based
`bar: int` and eighth-beat `beat: int`; `interval: str`, `consonance: int` (the
existing 0/1/2 roles), `pitch: str`, `figure: str`, `strong: bool`, `allowed: bool`,
`local: List[PanelFinding]`, `findings: List[PanelFinding]`, and `notice: str`.
The strings describe the supplied moving voice. Findings may contain other
bars: the renderer, not the caller, enforces the active-bar rule. Global verdicts
belong to the critic card, outside this column.

## The exposition

`subject` owns short, rhythmic modal lines, their independent validator and
bounded seed enumeration. `answer` compares spelled transpositions and the
single tonal head mutation. `counter` samples the union of two moving attack
timelines and checks the pair above and below the octave. `exposition` owns the
given subject and the two independent written lines; `session.voice` and
`session.beats` are the active desk, copied back before switching, judging,
rendering or playing. A reference never bypasses a judge.

`fuguepage` uses the shared staff/head API for the Book VI page, entry labels,
critic and end card. The exposition has two successive six-bar spans: subject
alone, then answer with continuation. Its named three-track part uses explicit
rests, preserving `ear`'s output owner. The clock is twelve wholes, not the
subject's ten attacks. No third entry is implied by the three track names.

Progress version 3 stores seven best-star counts, reads version 2 with a zero
seventh count, and version 1 with zero sixth/seventh counts. The sixth count is earned only after all three tutorials pass.
The current three tutorial scores live in the session; a completed sixth-book
light persists, but an interrupted tutorial sequence restarts at its first
page. Replay keys 26 (book-6) and 27 (voice-switch) append to the old vocabulary.


Book VI supplies `staff.PanelData` through `exposition.status`. One
`session.selection` resolves the editable voice's event and onset time.
All six books' Left/Right navigation selects notated events, with no offset
in State, Selection or undo history. The pitch edit, audition, caret and status
all consume that selection.
The merged timeline positions both voices, but an attack in the other voice
does not create a new editable selection. Joining, splitting, dotting, tying,
resting and undoing keep the selected event explicit.

Interval and figure sample the other voice at the selected onset; both finding
lists are restricted to the active bar. Enter opens the complete verdict.
Entry names occupy the reserved header. A clipped high pitch has a `!` marker,
leaving exactly one `^` caret. The selection census checks every event in both
desks at both sizes and tiers, then applies Up/Down and undo to verify the event
that really changed. Tied chains are checked as chains, not mistaken for stray
edits. The same census covers every preset and twelve mode/side pages in I–V,
including seven rhythm/register scenarios, both sizes and tiers.

## The player's cantus

The seventh title entry and `--book 7` open the same session editor with one
whole per event. `cantus_written=false` means `voice` is the player's single
line. The composition verdict calls `theory.validate` directly; there is no
second melodic checker, generator exception or historical waiver. `cantuspage`
draws that voice with the shared paper, fixed-clef staff/head and status column.
The complete critic card is scrollable, with every original tutor reason and bar.

`theory.shape_measures` exposes the generator's unchanged numeric ranking:
`100 - 3*abs(3*zero_based_summit - 2*length) + 4*interval_size_count`.
The card also shows rising/falling motion counts and their balance gap. Balance
is a hard admission rule, not an extra scoring bonus. `theory.shape` delegates
to those same measures, preserving every existing candidate score and order.
A melody alone earns no stars.

Confirming a legal card copies the exact written pitches to `cantus`, marks
`cantus_written=true`, clears undo and opens the ordinary first-species editor.
The chosen upper/lower voice starts unsolved; `first.check`, not a reference or
search result, judges it. The scrolling rhythmic layout keeps eight-to-sixteen
whole-note lines legible. A completed legal pair earns the seventh best-star
count. No bounded solver may reject or silently rewrite a legal player melody;
there is no promise that every player-written line admits a solution on both
sides. Change the line or chosen side if it makes an impractical study.

Length edits and pitches share the existing note/beat/selection undo transaction.
Mode and side choices are separate controls. `h` plays the single written line
before acceptance and the exact two-voice pair afterwards, with the same owner
and one-second whole-note clock. Replays contain only ordinary keys; no written
cantus or accepted verdict is injected from a file.

## Audition witness boundaries

`--trace` reports cumulative successful grid-write byte counts after complete
frames. The storm row applies each exact byte prefix through the terminal model
and independently derives its expected full state from the ordered recorded
sharp keys. Several presses can share a carrying frame; all are accounted for,
with that batch's exact final parity. A terminal read containing two writes is
not mistaken for one frame. Zero-byte even-parity batches still require their
completed frame boundary. The forty-key and seventy-ms p99 requirements remain;
a failed intermediate frame cannot be excused by a later correct final screen.

The p99 is from the parent's key write to its receipt of both complete terminal
bytes and their boundary trace, not the game's `inner_us` read-to-frame timing.
A separate joined owner-observer thread samples real child pids, with a 20-ms
pause between polls. Slow process-table commands cannot block key delivery or
pty reads and turn the intended 20-Hz stimulus into catch-up bursts. Owner count
must still be at most one, all forty expected states must match, delivery must
span at most two seconds, and observed p99 must stay within 70 ms. Measurements
retain actual send gaps, game-inner timing and observer timing separately.

Book VI readiness is likewise a state condition, not a sleep: alternate-screen
entry precedes the engine's bounded keyboard negotiation. The right-then-up row
awaits the exact complete independently rendered initial glyph/style frame
before sending either key. The cold-initial row deliberately returns the pty
constructor at terminal entry while negotiation is pending; no timeout or game
startup sequence is changed to satisfy it.
