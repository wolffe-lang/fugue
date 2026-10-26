# Replay

Fugue uses lair's `pk 1` text format: seed, rich/plain tier, size and tick-stamped
keys. The optional start value selects a page: 0 is seeded, 1–3 the tutorials,
99 the title art fixture, 101–103 a tutorial recording that begins on its title,
and 1000 a seeded recording that begins on its title. These are initial-state
selectors, not injected notes or trusted solutions.

Keys are `up down left right octave-up octave-down sharp sound hear check undo
new retry quit interrupt`. Inputs at the same tick retain file order. An arrow
is recorded as it arrived, not reconstructed from the final score. The score
comment is recomputed from the notes; a mismatch prints UNVERIFIED and exits 1.
Malformed replays exit 2.

```
fugue --record my-answer.pk
fugue --replay my-answer.pk --ticks 400
fugue --headless --script my-answer.pk --frames 400 --every 30 --dump frames
```

`tests/replays/solved-80.pk` is an actual pseudo-terminal recording of the first
original reference solution, verified at three stars. `tests/cases/preset-*`
are authored ordinary-key scripts, not claimed as recordings. Their listening
frames show each note lighting in order; their final frames are three-star
cards. `critic-*` and `title-*` exercise those screens at both sizes. `staff-*`
exercise a seeded cantus above the player. The art study compares margin names
and the drawn clef on both tiers and sizes. `verdicts/rules.txt` records the
actual judge's complete named findings for the legal reference and each hard
vertical-rule mutation, on both compiled backends.

Headless output is silent and deterministic. Live replays audition through the
same prepared-note adapter as live input. `--apply` feeds terminal bytes through
the engine's model; its agreement rows compare live and headless cells, including
styles and restored terminal modes. The fixed layout is not changed by a window
resize, and Fugue does not currently record resize events.

## Later books

Books II–V wrap the old start selector as `10000 + book*2000 + start`.
Thus 14001 is Book II's first tutorial, 14101 its title-start recording, and
21000 is a Book V seeded recording beginning at the title. All Book I values
remain unchanged. The appended vocabulary is `book-1` through `book-5`, `desk`,
`split`, `join`, `tie`, and `rest`. Rhythmic edits are recorded as keys, never
as a trusted completed score.

A recording can include `# books fugue 1 a b c d e`, its five initial best-star
counts. This affects only the title's progress display. The notes, rhythm and
final score are still recomputed by the judge. Missing or malformed cosmetic
progress starts at zero. A daily seed is the UTC day count together with the
selected book; different books retain distinct replay start selectors.

The `book-5-eighths-*` cases are unfinished editor studies of a weak paired
subdivision, not claimed three-star solutions. The `book-*-preset-*` scripts
are authored solutions; `book-*-solved.pk` under `tests/replays` are actual
pseudo-terminal recordings, verified by recomputing their scores.

Book VI uses the same namespace: 22001–22003 are its tutorials and 22101–22103
are their title-start recordings. `book-6` and `voice` append to the key
vocabulary; no earlier key number changes. Progress comments now use
`# books fugue 2 a b c d e f`; old five-book version-1 comments still load,
with the sixth book unlit. A `voice` event changes the edit desk, never injects
an answer. The exposition lasts 360 ticks for the six-bar tutorial subjects.
