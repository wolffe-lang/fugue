# fg04 prediction (written 2026-11-01 21:52Z, before the first measurement and the first change)

Base: fugue trunk `4742c47e` (lair `df11d213`, wolf 0.2.36). Read so far: fugue#36, the three red
attempts of push run 41344575553 (logs and their `macos-evidence` artifacts), the four earlier red
push runs' logs, `src/fugue.lu`'s live loop, lair's `src/clock`, `src/input` and `src/term`, and every
fugue pty row.

## The cause

1. **All three reds at `4742c47e` are the row's, not the game's.** `fugue-cursor-same-frame` and
   `event-caret` (and `cursor-same-frame`, which shares the code) give a key recorded at tick T to the
   frame traced at T+1. The game applies the keys of a wake at the wake's first tick T and draws once
   after every due tick, so a catch-up wake traces its frame at T + due. The artifacts show it:
   attempt 1, press 19 recorded at 66, no frame 67 (drawn at 68); attempt 2, press 3 recorded at 19, no
   frame 20 (drawn at 21); attempt 3, Left at 26 drawn at 30 and two Lefts at 30 drawn at 35
   (`inner_us 288888`, a 289 ms stall of the game itself). The unaccounted press leaves every later
   frame expected one (three) events behind, which is the "caret one press ahead" the issue saw.
2. **A second fault, latent:** those rows take a frame's image as all of `s.out` at the moment the row
   read the trace line, not the game's write boundary (`trace output frame T bytes N`). A row that lags
   behind the game reads a later frame's bytes too. I expect it to appear under the forced stall as a
   frame one or more presses "ahead" with no unaccounted press.
3. **The game is right in every frame measured:** each carrying frame cut at its exact output boundary
   equals the headless replay of the game's own `--record` at that tick (glyphs and styles); every
   injected press is recorded once and in order; a frame that carries two presses shows the caret two
   events on, never one. 0 disagreements. No game fix is owed.
4. **`cursor-long`** maps keys to frames correctly (the first frame after the record tick) but has the
   same snapshot fault and two wall-clock claims: `frames > 1` (any catch-up wake is "late") and the
   70/100 ms wall bars (row-observed time, which includes the row's own delays).
5. **`enhanced-keys`**' "did not negotiate flags 11" is its own wall-clock settle: the constructor's
   0.3 s settle ends before a slow start writes the query, and the row then asserts. A row stalled for
   150 ms past the query also misses the game's negotiation window: that session is out of its case.
6. **`audition-storm`** (fixed by fg03 to cut frames at write boundaries) keeps wall bars: the 70 ms
   observer p99 and the 2 s send span. Its pre-fg03 reds (24/40, 8/40) were the frame accounting fg03
   fixed.

## Under the forced stall (the background QoS clamp, the row, the game and 2 or 3 busy loops)

7. trunk's 30 Hz rows (`cursor-same-frame`, `fugue-cursor-same-frame`, `cursor-long`, `event-caret`)
   go red in most runs at both levels, by the unaccounted-press line and the late-frame line.
8. trunk's latency bars (`cursor-long`'s 70/100 ms, `audition-storm`'s 70 ms and 2 s,
   `audition-hear-owner`'s 100 ms) go red at least sometimes at level 3.
9. The rows that type keys and read the screen after a fixed settle (`panel-right-twice`,
   `three-ledgers-below-and-back`, `selected-event-status`, `book-5-rhythm-edits`, `solved-record`,
   `book-N-record`, `fugue-*-record`, `fugue-end-card`, `fugue-cursor-panel-*`, `fugue-right-then-up`)
   go red at the heavier level only, by a stale screen.
10. `enhanced-keys` goes red at least once by its negotiation line.

## The fix (predicted shape)

11. In the rows only: one trace-keyed injector shared by every row. Each write waits for the game's
    trace, is acknowledged by the game's own trace (its carrying frame, or the second output frame after
    the write), and is judged at the exact output boundary. Batches are cut at key boundaries into
    writes the game reads whole. The 30 Hz bursts become one press a tick by the trace. A session a
    stall pushes out of its case (the negotiation window missed, a host stall during a latency sample)
    is driven again, up to a bound, every re-drive printed; a case never realised is `SCHEDULE`; no
    re-drive forgives a disagreement.
12. Rows whose stderr shares the terminal (`quiet-audio-page-change`, `quiet-player-stderr`, the
    `fugue-junk-*` rows, the storm's reference session) cannot carry `--trace`; they get acknowledgement
    by an observable instead (the exact replayed frame, the owned player's process), with a bound.
13. No `src/`, case, golden, replay, engine, `lair.pin`, toolchain, `.github/` or `tools/check*` byte
    moves; Footprint: module. The maintainer's feel is untouched because the game is untouched.

## The proof

14. 20 runs at each of two stall levels (2 and 3 busy loops): trunk's rows red at least once at each
    level; the head's 20 of 20 green at both.
15. The plant (`fg04-plant-*`: the injector's acknowledged tick read off by one) is red by name.
