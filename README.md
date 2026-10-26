# fugue

| Machine | Display | Sound |
|---|---|---|
| macOS arm64 | Rich or plain terminal, at least 80x24 | Prepared WAVs through afplay |
| Linux x86-64 | Rich or plain terminal, at least 80x24 | WAV sink; no audio server required |
| PAX | Not integrated yet | Not integrated yet |

A cantus firmus is given on a manuscript staff. Write the voice against it,
note by note, hearing each pitch as you place it. The critic names broken rules
by bar. Legal answers pass; contrary motion, steps, shape and variety earn stars.

**Book I is playable:** first species, three original tutorial pages, then seeded
exercises in six modes with the cantus below or above. The remaining species and
the fugue chapter are planned, not implemented. Seeds are reproducible, not
unique: two seeds can choose the same melodic candidate.

## Build and play

```
tools/fetch-lair
.lair/tools/fetch-toolchain
.lair/tools/build --release
target/fugue
```

The whole pinned compiler archive, runtime and standard library are verified by
digest. The engine is pinned by commit in `lair.pin`; its modules are staged in
`.lair/`, never taken from a moving branch. The implementation uses wolf-std and
that engine only.

Enter opens the manuscript. Left/Right choose a bar; Up/Down write a note;
Shift-Up/Down move an octave. Space auditions, h hears both voices, Enter checks,
u undoes, n turns the page, and q or Escape quits. The permitted cadence sharp
is #. Listening locks edits until the highlighted pass ends; quit still works.

```
target/fugue --seed 7 --size 120x40
target/fugue --daily --plain
target/fugue --mute --record my-answer.pk
target/fugue --replay my-answer.pk --ticks 400
target/fugue --script my-answer.pk --frames 400 --sound-replay my-answer.pcm
```

`--mute` or `FUGUE_SOUND=0` disables audio. On Linux,
`FUGUE_WAV_DIR=./auditions target/fugue` retains the rendered WAVs. The plain tier
uses ASCII and sixteen colours with the same geometry as rich. Some terminals'
CSI-u keyboard mode is not yet decoded by the pinned engine; legacy Enter and
arrows work.

## Tests

```
tools/check                         # local host, memory-gated on macOS
.lair/tools/in-container tools/check-linux
.lair/tools/in-container tools/check-perf
```

The gate includes 71 checked tests, native and release builds, both-tier goldens
at 80x24 and 120x40, thirteen pseudo-terminal rows, per-rule verdicts, a 300-line
generator census, a pitch/row/margin round-trip, continuous staff and bar-line
walks, a complete listening cursor and exact PCM golden, three three-star reference solutions, a real solved recording,
score-tampering refusal, and a both-way glyph inventory. PR CI runs Linux; the
full tier adds macOS and performance. Six cited Fux cantus firmi are historical
test oracles only, never playable levels or source material for game music.

Read [Theory](docs/THEORY.md), [Keys](docs/KEYS.md), [Art](docs/ART.md),
[Sound](docs/SOUND.md), [Replay](docs/REPLAY.md), and [Design](docs/DESIGN.md).

Fugue runs on [lair](https://github.com/wolffe-lang/lair), alongside pack, cub
and trail.

## Licence

GPL-3.0-only, with the wolf Training Data Permission (`LICENSE-TRAINING-DATA`).
