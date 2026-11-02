# fg04 — the paced rows: fugue's macOS pty rows keyed to the trace (fugue#36)

fugue's macOS job went red on trunk push runs, on a different pty row each time, and green on the
scheduled runs and at labelled `tier full`. **The fault was the rows' in every case measured.** They typed
by wall-clock sleeps, read screens after fixed settles, and gave a key recorded at tick T only to the frame
traced at T+1. The game applies every key it read on a wake at that wake's first due tick, steps every due
tick and draws once, so a late wake traces its frame at T + due, and two presses read on one wake share a
frame. The game
drew exactly what its own recording says in all 7,817 carrying frames compared (CI's red case, and trunk's
rows unloaded and under the forced stall). Every fugue pty row now types through one trace-keyed injector
(`tests/paced.py`). No game, engine, pin, case, golden or CI byte moved.

## Before / after

**The three red attempts of push run 41344575553** (`notes/fg04-evidence/ci-reds-41344575553.md`, the
attempts' own recordings and the attempt-3 capture in `ci-41344575553/`):

| attempt | row, case | what the game did | what the row did |
|---|---|---|---|
| 1 | `fugue-cursor-same-frame` `1-120-rich-mute` | Left recorded at 66 drawn at 68 (a two-tick wake) | found no frame 67: press 19 unaccounted, press 20 expected one event behind |
| 2 | `fugue-cursor-same-frame` `0-120-plain-sound` | Right at 19 drawn at 21; two Rights read on one wake at 21 | press 3 unaccounted; presses 4–17 expected one event behind (4/20 aligned) |
| 3 | `event-caret` `book-5-80-plain` | `inner_us 288888`: Left at 26 drawn at 30, two Lefts at 30 drawn at 35 | three Lefts unaccounted (14/17); every later frame three events off |

The attempt-3 case, replayed (`measure.py analyse`, `ci-artifact-analysis/`): 17 of 17 carrying frames, cut
at their `trace output frame` boundaries, equal the headless replay of that session's recording, glyphs
and styles; 2 catch-up wakes (due up to 5), 1 frame carrying two presses, and the 3 keys trunk's rule
loses.

**Trunk's rows on the Mac** (`4742c47e`, one binary built from it, SHA-256 `cdc2dc20…a4aa9b`; every session
recorded by `measure.py`, the rows unchanged; `before/`):

| condition | trunk's rows | carrying frames, the game against its recording | catch-up wakes (max due) | frames carrying 2+ presses | presses trunk's rule loses |
|---|---|---|---|---|---|
| unloaded | 40 of 40 green | 3,504 of 3,504 agree | 0 (1) | 26 (the rows' own batches) | 0 |
| clamp + 2 busy loops | red: `fugue-cursor-same-frame` (12/20 accounted), `quiet-player-stderr`, `enhanced-keys` | 2,124 of 2,124 agree | 7 (18) | 185 | 8 |
| clamp + 3 busy loops | red: `cursor-long` (5 late presses, frame max 4, wall max 240.6 ms), `enhanced-keys` | 2,172 of 2,172 agree | 3 (4) | 162 | 5 |

Each red, by cause:

- `fugue-cursor-same-frame`, `event-caret`, `cursor-same-frame`: the `T+1` attribution above. The
  coalesced frames are right: two Rights read on one wake move the caret two events in that frame, every
  time (the replay agrees in all of them).
- `quiet-player-stderr` (842 text cells, 36 style rows "changed"): the row's `before` image was read 0.15 s
  after the alternate screen opened, and the game's first frame comes after its 150 ms keyboard
  negotiation; in the clamp it came later than 0.15 s, so `before` was the blank screen. No afplay text is
  in the capture (`Error:` and `AudioQueueStart` absent).
- `enhanced-keys` ("did not negotiate flags 11", 40767610212's line): the row asserted after the session
  constructor's 0.3 s settle. It then left that session running: the pty's holder keeps the master open
  and never reads it, so the game blocked writing a full terminal and never saw a quit (two such games,
  one per stalled run, ended by their pids, below).
- `cursor-long` (40767523484's line): five presses drawn by one four-tick catch-up wake are "late", and the
  wall bars are row-observed times that include the stall.

**The stall itself.** `notes/fg04-evidence/stall.py` (pk09's, copied) runs the rows, the game and N busy
loops in macOS's background QoS clamp (R-fg04-4). Measured with `band.py`, the clamp runs on about six
cores (5.8 cores' throughput from six loops on; `band.txt`), so two and three loops never starve it; the
reds come from the clamp's slower cores and their wake latency, and the game itself was held up to 1.2 s
(`inner_us` 1,227,700). One more finding: macOS coalesces `select(2)` and `sleep` timeouts in the clamp by
up to 200 ms (median 163 ms at a 30 Hz wait) but not `poll(2)`'s (2 ms) or kqueue's, and the game's wait
behaves like poll: its ticks stayed on time unloaded in the clamp while a Python `select` loop beside it
woke 160 ms late. The injector and its stall probe therefore wait in `poll`.

**The fix** (`tests/paced.py`, and every row file). The injector writes a byte only once the game has drawn
(its first frame, then the acknowledgement of the previous write) and, when a row schedules it, once the
trace shows the tick before its target. A single key is acknowledged by its carrying frame (the first
`carries_key` line after the write: nothing else is outstanding); any other write by the second output
frame traced after the write, whose wake read after the write (writes are cut at key boundaries to at most
256 bytes, what the game reads a wake). Frames are cut at their exact `trace output frame` boundary. After
the session, each recorded key is placed in the first carrying frame after its record tick, and that must
be a frame its write was acknowledged by (`verify`, `ACK:` lines); the bytes after the last frame must be the
leave bytes. A late byte is input, never a verdict; a session a stall pushes out of its case is driven
again, up to four sessions, each re-drive printed, `SCHEDULE` if never realised; no re-drive forgives a
disagreement. A row that raises ends the sessions it left running (`guarded`). The 30 Hz bursts are one
press a tick by the trace.

**The proof under the forced stall** (`notes/fg04-evidence/proof.sh`; the clamp with 2 loops, then with 3;
for each level 20 runs of the head's rows at `c6c1cfc` and, before head runs 1, 5, 9, 13 and 17, a run of
trunk's at `4742c47e`, interleaved so both meet the same machine, hour and load; each run its own locked run;
one binary for both trees. The rows: `cursor-same-frame`, `event-caret`, `cursor-long`,
`fugue-cursor-same-frame`, `audition-storm`, `audition-hear-owner`, `quiet-player-stderr`, `enhanced-keys`:
every row trunk's measurement reddened and every row fugue#36 names. `proof/`, each run's pty log,
`proof/summary.txt`):

| level | rows | runs | red | red rows (runs) |
|---|---|---|---|---|
| clamp + 2 | trunk's | 5 | **5** | `enhanced-keys` (5), `cursor-same-frame` (3), `quiet-player-stderr` (3) |
| clamp + 2 | the head's | 20 | 3 | `audition-hear-owner` (3): the 100 ms bar only, below |
| clamp + 3 | trunk's | 5 | **5** | `enhanced-keys` (5), `cursor-long` (2), `quiet-player-stderr` (2), `cursor-same-frame` (2), `event-caret` (1) |
| clamp + 3 | the head's | 20 | 10 | `audition-hear-owner` (10): the 100 ms bar only, below |

The head's other seven rows were green in all 40 runs: 280 of 280 row verdicts. No session was re-driven, no
latency bar skipped, no `SCHEDULE`: 28 of 28 enhanced sessions negotiated in every run, every storm was
delivered, and the stall probe set aside 36 of 25,600 `cursor-long` presses at clamp + 2 and 39 at clamp + 3
(the host's worst stalls 78.5 and 284.5 ms), the bars holding on the rest. Each failing trunk run that
abandoned an `enhanced-keys` session had its game ended by its recorded pid (`ROWS orphan:` lines).

**`audition-hear-owner`'s 100 ms** (R-fg04-7). The head's reds were all `h did not kill and reap the audition
within 100 ms ... the host on time`, at 100.4–107.0 ms (clamp + 2) and 100.8–136.7 ms (clamp + 3). At `096a000` I
had replaced the row's observer, a `pgrep -P` spawned in a loop, with a check of the audition's own pid, so the
time read was the audition's exit and no longer the observer's: 14–50 ms unloaded, 30–137 ms in the clamp, whose
slower cores slow the kill-and-reap path itself (no wake probe sees that). trunk's row counts a `pgrep` begun
before 100 ms as within the bar even when its answer comes later, and passed the same condition in all 10 trunk
runs at 94–119 ms. So the precise observer had tightened the claim. `797e747` restores trunk's measurement
exactly, and adds what the bar stands for in a form no host speed changes: the audition must be gone before the
whole piece's WAV exists (stop before render). That row, 20 runs a level at `797e747`
(`proof-hear-797e747/`): clamp + 2 **19 of 20**, the red at a poll begun at 143.7 ms with the probe reporting no
late wake; clamp + 3 20 of 20 (one session driven again, the host 719 ms late in its window).

**The probe's blind start, found by that red.** The rows start the stall probe and open their window at once
(`audition-hear-owner` writes h on the next line), and a Python probe runs only 15–24 ms after its `Popen` in the
clamp (8.6 ms median unloaded; `probe-gap-36e202fe.log`, 20 starts a level). So a stall in a window's first ~20 ms
read as "the host on time", and the probe's own start-up ran on the clamp's cores inside the window. `c3c8dab`
makes the constructor return only once the probe's script runs (its `start` line), and counts any stretch of a
window before that as late, never on time (red first at `722b70f`: `red-first-probe-722b70f.log`, two rows
`AttributeError`, then green at `ed7388d`). The change reaches only the three rows that use the probe, so they were
proved again at the final code head `401367f` (`proof-probe-401367f/`, 20 runs a level, each its own locked run):

| level | rows at `401367f` | runs | red | the bars |
|---|---|---|---|---|
| clamp + 2 | `audition-storm`, `audition-hear-owner`, `cursor-long` | 20 | **0** | storm p99 at most 45.7 ms over 21–40 presses a run the host ran on time; h's audition seen gone by polls begun at 28.1–86.9 ms; `cursor-long` judged on 25,371 of 25,600 presses (the probe's worst stall 1,275.7 ms), frame max 1, wall p99 at most 47.9 ms |
| clamp + 3 | the same | 20 | **0** | storm p99 at most 51.1 ms over 30–40 presses; h's audition gone by polls begun at 21.0–99.0 ms; `cursor-long` judged on 25,490 of 25,600 presses (worst stall 249.5 ms), frame max 1, wall p99 at most 40.9 ms |

The other five rows use no probe, and none of their code changed after `c6c1cfc` (`git diff c6c1cfc 401367f` touches
`tests/paced.py`'s probe, `tests/ear_rows.py`'s hear-owner row and the unit files only), so their 200 verdicts at
`c6c1cfc` are verdicts of the final head's code. At `401367f` no session was driven again, no bar was skipped and
nothing reached `SCHEDULE`. **So every head row is green in 20 of 20 runs at both stall levels at the final
code head, and trunk's rows went red in 10 of 10 runs.**

The same head before this pass's last fixes (`9c2a7b94`, all 40 rows, one run a level, `head-9c2a7b94/`) was
green at all three levels but for two rows since fixed. The final-head gauntlet (every row, unloaded) is
green.

**Every pty row, and what it timed by the wall clock** (the 40 fugue rows on macOS; Linux runs the same
code, with `linux-audition-sink` for the three Mac sound-owner rows):

| row | trunk | now |
|---|---|---|
| `editor-ear`, `hear-whole-is-played`, `book-5-ear` | 0.2–0.3 s settles after Up, Down, h, Enter | each key acknowledged; the bounded waits on the WAV file and the player lines kept (liveness) |
| `title-quit`, `staff-quit`, `card-quit`, `escape` | 0.1–0.2 s settles | first frame awaited, each key acknowledged; the lone ESC left to the game's 50 ms timeout |
| `solved-record` | 40 ms settles; the card read 40 ms after the check key | the card read at the check key's carrying frame |
| `panel-right-twice`, `three-ledgers-below-and-back`, `selected-event-status`, `book-5-rhythm-edits` | 0.07–0.3 s settles, then the screen | the screen at the acknowledging frame |
| `book-2..5-record` | a batch, 11 s of wall time for the hearing, then Enter | the hearing waited out in 330 of the game's ticks from h's frame; the card at Enter's frame |
| `cursor-same-frame`, `fugue-cursor-same-frame` | 30 Hz by wall time; a key at T matched to frame T+1; frames as held bytes | one press a tick by the trace; each key in its carrying frame; exact boundaries |
| `event-caret` | 80 ms settles; T+1; held bytes | the same |
| `cursor-long` | 30 Hz by wall time; held bytes; `frames > 1` and the 70/100 ms wall bars on every press | one press a tick by the trace; every press's frame judged; the latency claims on the presses the stall probe shows the host ran on time (R-fg04-3) |
| `cached-arrow-auditions` | 50–100 ms settles | each key acknowledged |
| `quiet-audio-page-change` (stderr on the terminal) | 1.0 s settle | the exact replayed first page, then the exact replayed next page, awaited (liveness) |
| `fugue-exposition-record`, `fugue-two-desks-record`, `fugue-end-card` | 40–600 ms settles; 1.1 s, 6.2 s and 6.2 s of wall time through the auditions and the exposition | acknowledged keys; 33, 186 and 372 of the game's ticks from h's frame |
| `fugue-junk-*` (stderr on the terminal) | 0.65 s settles, a 5 s poll, 13.5 s of wall time for the hearing | each state awaited exactly (liveness); the hearing's own frames left, then the after-hearing state reached |
| `fugue-press-budget` | 0.5 s settles | each key acknowledged (the row already read its carrying frame) |
| `fugue-cursor-panel-80/120` | 0.2–0.5 s settles | the panel at the acknowledging frame |
| `fugue-right-then-up`, `fugue-cold-initial` | a 30 s poll for the first frame, then 0.2–0.6 s settles; 600-byte batches | the first traced frame compared exactly; keys acknowledged; batches cut to whole keys |
| `quiet-player-stderr` (stderr on the terminal) | `before` 0.15 s after the alternate screen; 0.7 s, then the screen and the children | Right (it auditions nothing) after Space: the exact replayed frame of Space then Right is the acknowledgement and the damage check; the failed player must be gone (liveness) |
| `audition-storm` | 40 presses in 50 ms wall slots; the 2 s send span; the 70 ms p99 on every press | 40 presses at 20 Hz in the game's ticks, written as each falls due (a late wake reads several, accounted by the recording); delivered if each was written within 0.5 s of falling due; the 70 ms p99 on the presses the host ran on time (R-fg04-3) |
| `audition-hear-owner` (stderr on the terminal) | Space then 0.12 s; the retire within 100 ms | Space acknowledged by its owned audition; the retire and its order (the audition gone before the whole piece's WAV exists) judged always; the 100 ms, measured as trunk measured it, when the host ran on time (R-fg04-3, R-fg04-7) |
| `own-cantus-session`, `own-cantus-fux-keys` | 0.1–0.2 s settles, then a 5 s poll for the state | the acknowledging frame must be the exact headless state |
| `enhanced-keys` | asserted the negotiation after a 0.3 s settle; releases checked 40 ms later | the stand-in answers while the session drains; a missed negotiation is driven again; releases acknowledged by the second frame; the hearing's frames compared at the same hearing tick |

The engine's rows (`quit`, `ctrl-c`, `trap`, `agree-rich`, `agree-plain`) are lair's, in `.lair/tools/pty`:
they type with 80 ms settles but judge only exit status, the closing line, the restored terminal and a
replay, which no timing can redden. They are not this repo's code and are unchanged.

## Forbidden

No game code (`src/`), case, golden, replay, engine, `lair.pin`, toolchain, `.github/` or `tools/check*` change:
`git diff 4742c47e -- src tests/cases tests/goldens tests/replays lair.pin .github tools/check tools/check-linux
tools/check-perf` is empty, so the maintainer's feel is untouched in every case. The injector's unit rows run in
`tests/test_storm_frames.py`, which `tools/check` and `tools/check-linux` already run. No other game's code or
material. No label, merge, tag, release, issue filed or closed; no CI waited on, re-run or cancelled; no
attribution trailer. The planning repo and `~/.claude` were not written; kasumi was not touched; hasu was only
read (its README and its block waiters). On the Mac every build and run was behind the mkdir lock and its
8 GiB gate (`~/lanes/fg04/run`), from a worktree pinned to its commit (`build-<sha>`, the evidence tools from
`evtools-<sha>` copies of committed files), with the 60 s turn after every release; `HOME` and `TMPDIR` were
the lane's; the maintainer's MLX server was never touched, nor `~/.cub/`, `~/lanes/play/` or
`~/LocalLLM/Projects/`.

**Processes ended.** Two games trunk's `enhanced-keys` row abandoned in my measured runs (clamp+2: holder
67030, game 67032; clamp+3: holder 76602, game 76604) were ended by their exact pids, the game with SIGKILL
after SIGTERM could not reach it (it was blocked writing a terminal its holder never read); each holder then
reaped and exited. No process group was signalled, no runner of mine was killed. From then on the harness
records every session's holder and game, and `locked-rows.sh` ends any such game by its recorded pid only.

**One lapse, reported.** At 17:13 the injector's first unit run used Python's default temp directory, which on
this Mac is under `/var/folders`: eight `paced-test-*` directories (each a stand-in game script and its
recording) were created there. I removed exactly those eight paths a minute later, and the rows have written
under the checkout's `target/` since (`tests/test_paced.py`'s `SCRATCH`), with `TMPDIR` set to the lane's for
every command.

## Prediction

Committed before the first measurement and the first change: `6fe898b`, `notes/fg04-evidence/prediction.md`.
Scored:

1. The three reds are the row's `T+1` attribution, the game drawing a late wake's keys at T + due: **hit**
   (the artifacts, and 7,817 carrying frames that agree with the game's recordings).
2. A latent second fault, frames taken as the bytes the row held: **not shown.** The trunk rows that use it
   (`Frames`) bypass the harness's read hooks, so the first runs logged no read times for them, and none
   of the reds measured needs it: every one is explained by the attribution alone. The injector cuts every
   frame at its boundary anyway.
3. The game right in every frame, coalesced frames included: **hit**, 0 disagreements; a frame carrying
   two presses moves the caret two events.
4. `cursor-long`'s wall-clock claims: **hit** (clamp + 3: five presses in one four-tick catch-up wake, the
   wall max 240.6 ms).
5. `enhanced-keys`' negotiation line is the row's settle: **hit.** Trunk's row asserted 0.3 s after starting
   the session and, when it raised, left the game running. The paced row, whose stand-in answers while the
   session drains, negotiated in all 28 sessions at each stall level with no re-drive
   (`head-9c2a7b94/L2`, `L3`): the game did not miss its own 150 ms window once.
6. `audition-storm`'s pre-fg03 reds were fg03's: **hit** (no storm red at this base, unloaded or stalled).
7. trunk's 30 Hz rows red in most runs at both levels: **missed.** One run a level reddened
   `fugue-cursor-same-frame` (clamp + 2) and `cursor-long` (clamp + 3); `cursor-same-frame` and
   `event-caret` stayed green in those runs. The clamp's six cores are not starved by two or three loops.
8. trunk's latency bars red at least sometimes at clamp + 3: **hit** (`cursor-long`).
9. The settle rows red at the heavier level: **missed**, but for one: `quiet-player-stderr` (its 0.15 s
   settle) at clamp + 2. The other settle rows stayed green in both stalled runs.
10. `enhanced-keys` red at least once: **hit**, at both levels.
11. The fix in the rows only, one injector: **hit.** Two more than predicted: a stall probe for the
    latency claims, and acknowledgements by state for the rows whose stderr shares the terminal (12).
12. **Hit**, with a correction found by the head's own first runs: the failing player of
    `quiet-player-stderr` ends faster than any process poll sees it, so Right (silent) became that row's
    acknowledgement (`development/`).
13. No `src/`, case, golden, engine, pin, toolchain, CI or `tools/check*` byte: **hit**; Footprint module.
14. The proof: **hit for trunk** (red in 5 of 5 runs at each level). **Missed for the head at first**:
    `audition-hear-owner` went red in 3 and 10 of 20 runs at `c6c1cfc`, and in 1 of 20 at clamp + 2 at
    `797e747`. It was met at `401367f`, after two fixes the proof itself found.
15. The plant red by name: **hit** (four unit rows and three pty rows, locally and in its run).

## Inputs verified

- Base fugue trunk `4742c47e1b7728619b9ef19cf942dafca73cc806` (r41q's record), worktree `~/lanes/fg04/fugue` on
  branch `fg04`; every run from a worktree pinned to its commit (`~/lanes/fg04/build-<sha>`), the trunk
  build `build-4742c47e`.
- Engine `df11d213785f7694bdf3f3572299abc550d8b903` (`lair.pin`, unchanged), staged by `tools/fetch-lair`.
- wolf `0.2.36 (wolfgang, pin 5adf3d9)`, aarch64-apple-darwin archive SHA-256 `b79d5584…cfa4aa632`; lupin
  0.1.58, `c1b02771…2c309ec055`; std `78b9d3cbc41d51db44d18c40b6694403644d1c83`: staged and digest-checked by
  `.lair/tools/fetch-toolchain` (`.wolf-bin/STAMP`).
- One binary for every run, built from `4742c47e` behind the lock (`build-4742c47e.log`): release SHA-256
  `cdc2dc20ab6d7f9c48a7f3f1f999603503ff03a1ad55cb17aea0b1d84977ea9b`, native `d8cf65a8…6aff`
  (`binaries-4742c47e.sha256`). `src/` and `lair.pin` are byte-identical at every commit of this branch, so the
  head's rows and trunk's rows ran the same game.
- Read: the lane rules of 10-31 with every 11-01 addition, the contract, RULES §1–§10, fugue#36 whole and the
  logs and artifacts of the three attempts of 41344575553 and of 40767523484, 40767610212, 40454232568 and
  40438976766; pk09's contract and pack's `notes/pk09-the-aim-window.md` (`stall.py` copied from it); cub's
  `notes/cb19-the-three-rulings.md`; fugue's fg02c and fg03 contracts and `notes/fg03-the-own-cantus.md`; lair's
  `tools/pty`, `src/clock`, `src/input` and `src/term` at the pin, `docs/KEYS.md`; fugue's `src/fugue.lu`
  (the live and headless loops), `src/session/session.lu` (`step`, `tick`, the hearing), every pty row file.
- README read against the pass: the terminal-row sentences moved and are refreshed in the README-only
  commit `53dcd9a`; the row counts (43 Linux, 45 macOS) and everything else are current.

## Rulings recommended (implemented)

- **R-fg04-1, where the fault is.** (A) the rows: every red measured is the rows' timing or attribution, and
  the game agrees with its own recording in every frame; (B) a game change (a frame per key, or one key a
  tick), which would move replays and the maintainer's feel with no fault to fix. **Recommend A.**
  Implemented: no game change.
- **R-fg04-2, the tick a late-read key gets.** (A) keep lair's clock (a late wake's keys on its first due
  tick, presses read on one wake drawn in one frame) and say so in `docs/KEYS.md`, as R-pk09-2 A did for
  pack; (B) a lair lane applies one key a tick. **Recommend A.** Implemented: the KEYS section.
- **R-fg04-3, the latency bars on a stalled host** (`cursor-long`'s late-frame rule and 70/100 ms bars,
  `audition-storm`'s 70 ms p99, `audition-hear-owner`'s 100 ms). (A) judge each on the presses whose window
  a stall probe shows the host ran on time (a process of its own doing the game's 30 Hz `poll` wait; a
  wake more than 5 ms late is a stall, where a quiet Mac stays under 3 ms), never forgiven there; a session
  that could not measure (more than half its presses stalled) is driven once more, and a bar no session
  could measure is a loud, counted SKIP naming the probe's numbers, while every frame and state is still
  judged; (B) the same, but an unmeasured bar is `SCHEDULE` (red): honest about the host, but a runner busy
  through two sessions reds the macOS job again, which is fugue#36; (C) trunk's: every press, red on any
  stall. **Recommend A.** Implemented. A note on what the bars now read: the injector writes each press just
  after a frame is drawn, so a press waits a whole tick for the next due tick (about 34 ms unloaded, where
  trunk's random phase read 10–27 ms); the bars are as strict as before or stricter. The probe vouches only
  for the time it ran: its constructor returns once it runs, and a stretch of a window before that counts as
  late (`c3c8dab`, the proof's second finding).
- **R-fg04-4, the forced stall on the Mac.** (A) pk09's background QoS clamp with 2 and 3 busy loops (the
  contract's levels), measured: the clamp's six cores are not starved by them, and trunk goes red at both
  levels anyway; (B) loops past the six cores, which starve the row itself (pk09's 12-loop finding);
  (C) hasu's one CPU, cb19's stress4 (16 jobs waited on hasu's blocks at this lane's launch). **Recommend
  A.** Implemented.
- **R-fg04-5, rows whose stderr shares the terminal** (`quiet-audio-page-change`, `fugue-junk-*`,
  `quiet-player-stderr`, `audition-hear-owner`). (A) acknowledge each key by the exact replayed frame or by
  the owned player it starts, with liveness bounds, as implemented; (B) a trace on its own descriptor
  (`--trace-fd`), a game change for a later lane. **Recommend A** now, B if the maintainer wants these rows
  traced too.
- **R-fg04-7, `audition-hear-owner`'s 100 ms on a slow host.** The game stops and reaps the audition before
  it renders (`ear.hear` calls `stop_audition` first). Timed exactly (the audition's own pid), that takes
  14–50 ms unloaded and 30–137 ms in the clamp, because the clamp's slower cores slow the kill-and-reap path,
  which no wake probe sees; trunk's observer (`pgrep` begun within 100 ms) reads the same runs as within the
  bar. (A) keep trunk's measurement exactly and add the host-independent order the bar stands for (the
  audition gone before the whole piece's WAV exists); (B) the precise time against 100 ms, which reds the
  clamped host in half the runs: a stricter claim than trunk's, the maintainer's to make; (C) a wider bar.
  **Recommend A.** Implemented (`797e747`). With the probe fixed (`c3c8dab`), the row passed 40 of 40 runs at
  `401367f`, with its audition seen gone by polls begun at no later than 99.0 ms. That is close to the bar
  under the clamp. A slower runner may yet show the 100 ms as the host's speed and not the game's; if it
  does, (B) and (C) are the maintainer's choice, and the order check holds either way.
- **R-fg04-6, the macOS leg before the merge.** `tier pr` runs the Linux leg only; the macOS rows that went
  red run at `tier full`. **Recommend** the orchestrator adds `full-matrix` at the final head (R-pk09-5's
  shape), so the paced macOS rows are seen green before trunk is.

## Evidence index

All under `notes/fg04-evidence/`.

- `prediction.md` (`6fe898b`).
- The harness: `measure.py` (runs a tree's own rows with every session recorded; `analyse` replays each
  session's recording headless and compares every carrying frame at its boundary), `stall.py` (pk09's
  forced stall, copied), `band.py` and `band.txt` (the clamp's cores), `locked-rows.sh` (one locked run;
  ends an abandoned game by its recorded pid), `series.sh`, `proof.sh`, `summarise.py`, `hear-timings.py`,
  `analyse-locked.sh`, `gauntlet.sh`.
- fugue#36's run: `ci-reds-41344575553.md`, `ci-41344575553/attempt-{1,2,3}/` (the recordings, journals,
  the attempt-3 capture and trace, each attempt's pty lines), `ci-artifact-analysis/` (its replay check).
- Trunk measured: `before/L0`, `before/L2`, `before/L3` (each run's pty log, the replay analysis and its
  per-session summary), `before/calib.log`, `binaries-4742c47e.sha256`.
- The injector's rows red first: `red-first-test-paced-eec74581.log` (at `eec7458`, before `paced.py`); the
  probe's two rows red at `722b70f` and green at `ed7388d`: `red-first-probe-722b70f.log`.
- The probe's start gap: `probe-gap.py` and `probe-gap-36e202fe.log` (20 starts unloaded, in the clamp, and
  at each stall level).
- The head's first run (`development/head-8ceabdab-L0-rows.log`, a local commit since rewritten): it found
  the failing player of `quiet-player-stderr` too quick for any process poll and the storm's row-lateness
  bound too tight for the owner sampler's GIL; both fixed before `9c2a7b94`.
- The head at `9c2a7b94` at all three levels: `head-9c2a7b94/L{0,2,3}/rows.log`; it found the quiet row's
  comparison of a later screen with a tick-2 frame (`b80c6ac`, `756b893`) and the hear-owner observer's
  slow `pgrep` (`eb891ad`, `096a000`).
- The plant: `plant/` (the unit rows and three pty rows, red by name).
- The proof: `proof/proof.log` (one line a run), `proof/<tree>-L<level>-<k>/rows.log` (each run's pty log),
  `proof/summary.txt`; `audition-hear-owner` at `797e747`, `proof-hear-797e747/`, the same shape, with
  `timings.txt` (`hear-timings.py`: the row's own numbers, one line a run); the three probe rows at the final
  code head, `proof-probe-401367f/`, the same shape.
- The gauntlet at the final code head: `gauntlet-401367f-steps.txt` (every `BEGIN`/`END` line, the binaries'
  digests) and `gauntlet-401367f.log.gz` (its whole log); the earlier ones at `c6c1cfc` and `797e747`, the same
  shape.

## Done-when

- [x] Measure first: the three red attempts read from their artifacts; trunk's rows reproduced red on the Mac
  under the clamp with 2 and 3 loops; each red's cause named; the game against its own recording in every
  carrying frame (7,817 frames, 0 disagreements).
- [x] The fix where the fault is: the rows. One trace-keyed injector, every fugue pty row through it (the
  table above); no game, engine, pin, case, golden or CI change.
- [x] The proof: 20 runs at each stall level. Trunk's rows were red in 10 of 10 runs. The head's five rows without
  a probe were green 40 of 40 (`c6c1cfc`), and its three probe rows 40 of 40 at the final code head `401367f`.
- [x] The plant `fg04-plant-ack` (`df5356f`) red by name, locally (`plant/`) and in its own run 41368981215
  (the Linux job 125035161262, the four `Protocol` rows); draft PR #37. Its base `c6c1cfc` holds the final
  head's injector byte for byte but for the probe, which none of the plant's red rows uses.
- [x] KEYS refreshed; README refreshed (README-only commit `53dcd9a`).
- [x] The gauntlet green at `401367f`, the code of the final head (every later commit is under `notes/`):
  16 steps, `.lair/tools/check` 227 passed and 45 pty rows ok with 0 SKIP, then 3 more on the native build;
  every `END` line in the PR body (`gauntlet-401367f-steps.txt`).
- [ ] `tier pr` green at the head, and (R-fg04-6) the macOS leg at `full-matrix`: the orchestrator's.
- [ ] Two green push runs after the merge, then fugue#36 closed: the orchestrator's.

Not done, plainly:

- The Linux rows were not run locally, stalled or not: hasu's blocks were held by other lanes' jobs when this
  lane began, and the contract asks for Linux only if needed. The Linux leg's evidence is the PR's `tier pr` run,
  and the plant's run 41368981215 shows that leg running the injector's rows (red by name there).
