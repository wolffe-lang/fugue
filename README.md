# fugue

| Machine | Display | Sound |
|---|---|---|
| macOS arm64 | Rich or plain terminal, at least 80x24 | Prepared WAVs through afplay |
| Linux x86-64 | Rich or plain terminal, at least 80x24 | WAV sink; no audio server required |
| PAX | Not integrated yet | Not integrated yet |

A cantus firmus is given on a manuscript staff. Write the voice against it,
note by note, hearing each pitch as you place it. The critic names broken rules
by bar. Legal answers pass; contrary motion, steps, shape and variety earn stars.

**All six books are playable:** note against note, two against one, four against one,
suspensions, florid counterpoint, and the fugue. Each has three original tutorial
pages, then seeded exercises in six modes. Book VI gives a subject, asks for
its real or tonal answer, then checks a countersubject on both sides of the
octave. Hear the subject alone, then the answering pair; finish the three
fugue tutorials to light the sixth book. **Book VII is your own cantus:** choose
a mode, write eight to sixteen whole notes, inspect the melodic critic and shape
score, then solve first species against that exact line, above or below.
The seventh book's stars come from the solved pair. Seeds are reproducible, not unique:
two seeds can choose the same melodic candidate. Every offered seed has a checked legal answer;
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

At the title, 1–7 chooses a book; Enter opens the current page. Left/Right
selects the previous or next notated event in every book, including rests;
Up/Down writes that selected note; the caret and bar/beat identify its attack;
Shift-Up/Down move an octave. Space auditions, h hears both voices, Enter checks,
u undoes, n turns the page, and q or Escape quits. The permitted cadence sharp
is #; in VI it cycles natural, sharp and flat anywhere.
In IV, t toggles a barline tie; in II and IV, 0 toggles the opening half rest.
In V, [ splits, ] joins, . dots, t ties to the next event, and r toggles a
rest without changing its length. Every edit is undoable. b returns to the books.
In VI, v changes the Answer/Countersubject writing desk.
In VII, m chooses the mode, [ adds a whole, ] removes the selected note, and v
chooses the counterpoint side. Enter checks the melody; Enter on its legal shape
card begins the unsolved two-voice exercise. n starts a fresh line.
Listening locks edits until the highlighted pass ends; quit still works.
Best stars are saved in `.fugue-state` (`FUGUE_STATE` selects another file).

```
target/fugue --seed 7 --size 120x40
target/fugue --book 4 --daily --plain
target/fugue --book 6 --size 120x40
target/fugue --book 7
target/fugue --mute --record my-answer.pk
target/fugue --replay my-answer.pk --ticks 400
target/fugue --script my-answer.pk --frames 400 --sound-replay my-answer.pcm
```

`--mute` or `FUGUE_SOUND=0` disables audio. On Linux,
`FUGUE_WAV_DIR=./auditions target/fugue` retains the rendered WAVs. The plain tier
uses ASCII and sixteen colours with the same geometry as rich. The game
negotiates kitty keyboard flags 11 when supported, including CSI-u controls,
and retains legacy Enter/arrows as fallback. Press and repeat each perform one
action; release does not edit. See Keys for protocol-fixture provenance.

## Tests

```
tools/check                         # local host, memory-gated on macOS
.lair/tools/in-container tools/check-linux
.lair/tools/in-container tools/check-perf
```

The gate includes checked rule and interaction tests, native and release builds,
and rich/plain goldens at 80x24 and 120x40. It checks eighteen three-star tutorial
references, actual solved recordings for all six books, score-tampering refusals,
terminal restoration, rhythmic two-voice PCM, and the glyph inventory. Fixed-clef
line/space mapping, grand staves, three-ledger walks, selected-event status,
partial measures and rhythm edits are exercised in both tiers. Every book has one
caret per selected notated event, including rests; the live diagnostics list only
the active bar, while Enter keeps the global verdict and counts. A real-pty
`cursor-same-frame` row checks single arrows and ten-key 30 Hz bursts, with and
without sound, in rich/plain at both sizes, retaining per-press frame evidence.
A 160-press whole-page traversal also checks p99 and worst-press
latency through held events and scrolling. An all-book real-pty row checks 408
arrow/audition keys against event onsets and attack columns at both sizes and
tiers. Audio rows join stderr to the
terminal for page changes and verify that arrow auditions reuse the note bank. A 30-page
census checks 1,254 initial/reference note rows and 24 synthesized fundamentals within 1%; exact
Book I PCM remains gated. The first
book retains its 300-line generator census; later books exercise twelve seeds
each, covering every mode and both voice positions. The later-species verdict
study pins 127 legal/illegal rows, and the classifier has seventeen explicit
figure rows. Book VI adds a 300-subject census, exact real/tonal checks,
independent inversion admission, a twelve-second played-exposition PCM,
three tutorial references and the end card. Book VI uses the same active-bar
status column and one caret aligned with the event Up/Down edits, with every-cell repaint checks after
page changes, voice switches, refusals and playback. Its event-selection census
checks 1,955 positions and 7,820 frame/edit pairs per backend, including unequal
rhythms, ties, rests and wide registers. The same census checks another 11,130
positions and 44,520 frame/edit pairs in I–V, with forward/backward traversal of
every preset and twelve seeded mode/side pages per book. The terminal harness has
42 rows on Linux and 44 on macOS. The new rows cover negotiated press/repeat/release
controls in all seven books, full own-cantus sessions and v2-to-v3 progress migration
at both sizes and tiers, and Fux's six cantus firmi entered by keys with their exact
existing oracle verdicts. Eighteen named critic-rule rows check the study's hard
rules. Sound-owner rows verify silent failing players, one
live audition through forty rapid accidental changes, h replacing an audition,
and Linux's single rewritten audition file. PR CI runs Linux; the full tier adds macOS and performance.
Six cited Fux cantus firmi are historical test oracles only, never playable
levels or source material for game music.


Read [Theory](docs/THEORY.md), [Keys](docs/KEYS.md), [Art](docs/ART.md),
[Sound](docs/SOUND.md), [Replay](docs/REPLAY.md), and [Design](docs/DESIGN.md).

Fugue runs on [lair](https://github.com/wolffe-lang/lair), alongside pack, cub
and trail.

## Licence

GPL-3.0-only, with the wolf Training Data Permission (`LICENSE-TRAINING-DATA`).
