# fugue

| Machine | Display | Sound |
|---|---|---|
| macOS arm64 | Rich or plain terminal, at least 80x24 | Prepared WAVs through afplay |
| Linux x86-64 | Rich or plain terminal, at least 80x24 | WAV sink; no audio server required |
| PAX | Not integrated yet | Not integrated yet |

A cantus firmus is given on a manuscript staff. Write the voice against it,
note by note, hearing each pitch as you place it. The critic names broken rules
by bar. Legal answers pass; contrary motion, steps, shape and variety earn stars.

**Books I–V are playable:** note against note, two against one, four against one,
suspensions and florid counterpoint. Each has three original tutorial pages,
then seeded exercises in six modes with the cantus below or above. The fugue
chapter is planned. Seeds are reproducible, not unique: two seeds can choose
the same melodic candidate. Every offered seed has a checked legal answer;
three stars are not promised for every seed.

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

At the title, 1–5 chooses a book; Enter opens the current page. Left/Right
moves by the book's smallest unit; Up/Down writes a note;
Shift-Up/Down move an octave. Space auditions, h hears both voices, Enter checks,
u undoes, n turns the page, and q or Escape quits. The permitted cadence sharp
is #. In IV, t toggles a barline tie; in II and IV, 0 toggles the opening half rest.
In V, [ splits, ] joins, . dots, t ties to the next event, and r toggles a
rest without changing its length. Every edit is undoable. b returns to the books.
Listening locks edits until the highlighted pass ends; quit still works.
Best stars are saved in `.fugue-state` (`FUGUE_STATE` selects another file).

```
target/fugue --seed 7 --size 120x40
target/fugue --book 4 --daily --plain
target/fugue --book 5 --size 120x40
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

The gate includes 120 checked rule and interaction tests, native and release builds,
and rich/plain goldens at 80x24 and 120x40. It checks fifteen three-star tutorial
references, actual solved recordings for all five books, score-tampering refusals,
terminal restoration, rhythmic two-voice PCM, and the glyph inventory. Fixed-clef
line/space mapping, grand staves, three-ledger walks, selected-event status,
partial measures and rhythm edits are exercised in both tiers. A 30-page
census checks 1,254 initial/reference note rows and 24 synthesized fundamentals within 1%; exact
Book I PCM remains gated. The first
book retains its 300-line generator census; later books exercise twelve seeds
each, covering every mode and both voice positions. The later-species verdict
study pins 127 legal/illegal rows, and the classifier has seventeen explicit
figure rows. PR CI runs Linux; the full tier adds macOS and performance.
Six cited Fux cantus firmi are historical test oracles only, never playable
levels or source material for game music.


Read [Theory](docs/THEORY.md), [Keys](docs/KEYS.md), [Art](docs/ART.md),
[Sound](docs/SOUND.md), [Replay](docs/REPLAY.md), and [Design](docs/DESIGN.md).

Fugue runs on [lair](https://github.com/wolffe-lang/lair), alongside pack, cub
and trail.

## Licence

GPL-3.0-only, with the wolf Training Data Permission (`LICENSE-TRAINING-DATA`).
