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
