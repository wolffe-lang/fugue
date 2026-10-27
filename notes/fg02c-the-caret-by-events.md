# fg02c — the caret by events

_Materialised from fugue#30's body at the merge (`7369f617`); the Codex wrapper writes no .md notes._

# fg02c — the caret by events


Final head: `7369f617a8abce673e1c8e425914a8cc13be94ba`. This five-section PR body is the lane record for materialisation on trunk; no Markdown report file was written.

## Prediction

Committed before implementation in `a734a55`, notes/fg02c-prediction.txt: expect hidden subdivisions on a held event, then one reachable caret position per editable event after the fix, with no golden change outside caret cells.

Reproduced with the unchanged fg01c Mac play artifact and the exact `--book 5 --size 120x40 --no-title` arguments, rich and plain, eight real Right presses. Zero-based columns after presses 0–8: **9,10,11,12,14,15,16,17,20**. Selected event indices: **0,0,0,0,1,1,1,1,2**. Selection is resolved from the displayed musical time against the shipped preset's onsets, corroborated by the compiled state traversal. Raw captures: /Users/mfwolffe/lanes/fg02c/before/; committed per-press journal: notes/fg02c-evidence/before-eight-right.json.

After the fix, final Mac real-pty presses 1–8 select indices **1,2,3,4,5,6,7,8**, at columns **14,20,25,31,35,39,43,48**, onsets **4,8,12,16,18,20,22,24**, identical in 120x40 rich/plain. Every frame has exactly one aligned caret and matching status. Journal: /Users/mfwolffe/lanes/fg02c/mac-final-target/pty/event-caret/measurements.json.

The initial event is actually a half rest, not the predicted whole: four positions there, eight on each whole elsewhere. The diagnosis holds, but that initial-value prediction was wrong. No-outside-caret golden changes was also too strong: selected onset/strong-beat text changes in eight seeded Book V frames, and six high-overflow markers become `!`. Engraving widths are unchanged. notes/fg02c-evidence/golden-audit.json enumerates every changed text cell.

## Forbidden

No lair, compiler/runtime, pin, loader, spec, CI workflow, package, memory/configuration or planning-repo change. No attribution trailer, label, merge, tag, release, issue filing or issue closure. Original game code and game-owned tests/docs only.

Linux work uses hasu block B under /home/mfwolffe/lanes/hasu-block-B.lock, the existing localhost/pack-ci:fbee7e864f7dbee6 image, taskset -c 6-11 inside, and --memory 12g. The Mac uses only /Users/mfwolffe/lanes/fg02c paths, its own HOME/TMPDIR and the scripted 8 GiB free+inactive+speculative gate. The model server and other lanes are untouched.

## Inputs verified

Read the whole contract, RULES sections 1–10, fg01b, fg02 item 7b and fg01c, README and cursor/player/replay docs. Base is fugue trunk 6ebdd69. Unchanged lair 57870143, wolf 0.2.35 / lupin 0.1.56 / bundled std 2386522e; complete previously verified archive pairs reused from fg01c. Mac driver/worker/interpreter/runtime/stamp digests and identities were read twice and matched. No source-built toolchain or package install.

Left/Right now changes `cursor` by exactly one event in the editable voice in all six books. Rests and tied events are selections. `Selection` contains only event and onset time; undo retains the event index, notes and beats, not an offset. Caret, status, pitch/rhythm edits and audition all resolve that event. Playback still follows sounding events and has no new navigation offset.

`grep -rn within src` leaves only four English strings: two subject-rule explanations and the two bounded-generation failure messages. State, Selection, Edit, the Book VI layout adapter and status API have no `within`. `session.editor_unit` is removed. Only the historical engraving-density arithmetic survives, privately as `manuscript.spacing_unit`, preserving existing widths rather than manufacturing selectable cells.

Recommendations, implemented as recommended:
- R-fg02c-1: retain existing engraving widths independently of navigation; no unrelated respacing.
- R-fg02c-2: reserve `^` for selection in every book; use `!` above the visible register. The new all-book census also found Book I's compact grand staff could omit its caret; it now uses the bar-number row fallback.
- R-fg02c-3: replace shipped authored time-slot inputs and recapture actual species recordings rather than silently claim old I–V replay semantics survived. Key IDs/envelope remain unchanged; old hidden-offset recordings are explicitly incompatible in docs/REPLAY.md.
- R-fg02c-4: the offline selection census grew from 1,955 to 13,085 positions (6.7x). Its inherited 180-second native subprocess watchdog expired, so only that offline command now gets 7×180 seconds. All other subprocess limits, live frame/latency bars and performance gates are unchanged. The named timeout is retained below; this is a harness allowance for additional work, not a green performance claim.
- R-fg02c-5: synchronize inherited Book VI witnesses with terminal entry and the exact complete expected frame, rather than fixed startup/page-preparation sleeps. Repaint polling has a five-second bound, compares every glyph/style with no masked region and preserves the first mismatching capture; independent live-key latency bars remain unchanged. Both tiers' focused rows passed before relaunch.

README read against the final change and refreshed in README-only commit `1f6bb68`: controls, 187 checked tests, all-book event census, 160-press long walk, and 39 Linux / 41 Mac terminal rows. Install/build/machine statements remain current.

## Evidence index

Implementation chunks:
- `a734a55` — prediction before the first implementation change.
- `674cc89`, `ae5afdc` — baseline reachable-position and attack-column witnesses, plus an unused-import correction before the successful baseline compile.
- `05e3834` — event-navigation, sole-caret, selected rhythm edits and stationary-audition regressions.
- `c510740` — event-only State/Selection/undo and caret/status consumers; adapt inherited latency oracles.
- `aa946ac`, `bad4e4f` — distinct overflow marker, event-input fixture migration and compact first-book caret fallback.
- `481f356`, `fa1bfa3` — documentation, formatter, reachable-count gate and first-book panel oracle correction.
- `1f6bb68` — README-only refresh.
- `5f4287a`, `5dff944` — fresh actual-input recordings and reviewed text/style goldens.
- `d1d21fe` — retained raw baseline, two plant logs and golden key-set/cell audit.
- `758e4ee` — test-only sound-owner fixture correction: the penultimate event is now one Left from the last, not eight hidden eighth steps. The source tree compiled for Mac is unchanged.
- `7081e97` — scale only the expanded offline census's subprocess watchdog; keep all live latency and performance bars unchanged.
- `7369f61` — wait for actual terminal entry and exact full-state repaint in inherited Book VI witnesses; no game source changed.

### Reachable-position census

Every one of the three shipped presets in each book has the same per-book counts below. Counts distinguish logical event/onset positions across viewport scrolling, not repeated screen x coordinates.

| Book | Before positions / editable events | After positions / editable events |
|---|---|---|
| I | 10 / 10 | 10 / 10 |
| II | 20 / 19 | 19 / 19 |
| III | 40 / 37 | 37 / 37 |
| IV | 20 / 19 | 19 / 19 |
| V | 80 / 21 | 21 / 21 |

Baseline log: notes/fg02c-evidence/before-census.txt. Post-fix developmental output: /home/mfwolffe/lanes/fg02c/development.log. The compiled census covers every preset plus twelve seeded mode/side pages in I–V, seven normal/rhythm/register scenarios, both sizes and tiers: **11,130 positions / 44,520 frame-and-edit checks**. It walks backward too. Existing VI coverage remains **1,955 / 7,820** in both available desks. The event checked is the event changed by Up/Down, including tied chains, with undo verified.

### Test-first, real input and goldens

The unchanged navigation fails `test_right_never_moves_the_caret_without_selecting_the_next_event`, the selected Book V rhythm-edit row and the stationary-attack row by assertion (notes/fg02c-evidence/tests-before.txt). The initial monolithic sole-caret test exhausted the checked step budget; it was split into six bounded book tests, not waived. The later full developmental suite is **187 passed, 0 failed/rejected/unsupported, 0 SKIP**.

The all-book real-pty row checks 408 actual arrow/audition keys per backend: eight Right, eight Left, Space, both sizes and tiers in Books I–VI. Each carrying frame must have exactly one caret at event N's attack column, an onset-derived matching bar/beat and no audition displacement. The independent attack map uses rhythm.onset and the event geometry, not session.step to predict the next selection. Linux release preparation is green in /home/mfwolffe/lanes/fg02c/preparation.log; native and final-head rows are in the final gate below. Book V split/join/dot/tie/rest act on the navigated event and undo returns to that event; inherited real-input rhythm rows remain.

New actual-pty recordings for II–V reached three stars, were replayed and recomputed, then committed. No edited authored file is presented as an actual recording. Golden inventory is **2,135 paths before and after, zero added/removed**, 250 changed files. The cell audit records the compact fallback caret cells, six overflow marks and eight onset-status frames; all `.sty` companions remain checked.

### Plants

Fixed code precedes both local plants; no plant CI dispatch or CI wait was used.
- Draft #28 / fg02c-plant-offset / `87ed268`: Right moves the drawn caret without moving the event. `test_right_never_moves_the_caret_without_selecting_the_next_event` fails by assertion, direct exit 1; 6 passed, 3 failed, no rejected/unsupported. notes/fg02c-evidence/plant-offset.log; original /home/mfwolffe/lanes/fg02c/plant-offset.log and plant-offset.exit.
- Draft #29 / fg02c-plant-double / `2d5b221`: two carets in one frame. `test_exactly_one_event_caret_book_five` and II–IV fail by assertion, direct exit 1; 4 passed, 5 failed, no rejected/unsupported. notes/fg02c-evidence/plant-double.log; original /home/mfwolffe/lanes/fg02c/plant-double.log and plant-double.exit.

### Exact-head gates and play

The exact-head Linux gate is running at 7369f617a8abce673e1c8e425914a8cc13be94ba. Durable pid **1011102**, /home/mfwolffe/lanes/fg02c/linux-gate.pid; source marker linux-gate.head, log linux-gate.log, completion marker linux-gate.exit (absent until done). It runs tools/check-linux (187 checked tests, both builds/goldens, all terminal/gameplay/pitch/PCM/census gates), native event-caret/cursor-same-frame/cursor-long/rhythm rows, then tools/check-perf. No pending job is claimed green. The expanded offline census makes this a potentially over-20-minute hasu job; this is the contract's durable pid/log/completion-marker handoff, not a completed local-gauntlet claim. The coordinator must read the completion marker and final log before accepting the gate.

Prior-head full gate at 758e4ee: checked tests, both builds/goldens, all 39 release terminal rows (including the corrected single-file audition sink), gameplay, species and pitch rows passed; then subprocess.TimeoutExpired stopped native `--fugue-cursor-census` at its inherited 180 seconds. Raw log and exit 1 are preserved in /home/mfwolffe/lanes/fg02c/linux-pre-watchdog-gate.log and linux-pre-watchdog-gate.exit. The watchdog commit changes only the offline census wrapper's allowance, not game source. The still-earlier gate's inherited eight-Left cadence failure remains in linux-pre-cadence-gate.log and linux-pre-cadence-gate.exit (1). Neither failed run is described as a complete green.

The following 7081e97 attempt ended on two intermittent inherited terminal-sampling rows before reaching the census: a first snapshot taken before terminal entry (`fugue-right-then-up`), and stale page-preparation snapshots (`fugue-junk-120-rich`). Original failures and direct exit 1 are preserved in /home/mfwolffe/lanes/fg02c/linux-pre-startup-gate.log and linux-pre-startup-gate.exit. The final test-only synchronization fix was then checked in **twelve focused rows**, native/release × all four junk sizes/tiers, right-then-up and Linux audition sink: all exit 0, /home/mfwolffe/lanes/fg02c/focused-startup.log and focused-startup.exit (0). Final full gate remains pending; this focused result is not substituted for it.

Exactly one Mac release play build succeeded at d1d21fe behind the **12.245 GiB** memory check. Binary SHA256 **0ed96312666e4bebe448d059499f3b8c8a762eeae919afb0407d9f8903b5cc6f**. Subsequent heads 758e4ee, 7081e97 and 7369f61 change only test fixtures/wrappers; all have the identical production src tree **d9bda6e6b2a0689fc5f6c7604b9d44f48e437c89**. The first equivalence pair is recorded in /Users/mfwolffe/lanes/fg02c/mac-source-tree-equivalence.txt, and the final tree was re-read directly with git rev-parse. No second release build was made or claimed.

The initial Mac pass verified the 408-key all-book row, 22-key bursts, every 160-key long case, selected rhythm edits/status and silent real failing players; only the inherited eight-Left cadence setup failed. That raw log/status and capture are retained as /Users/mfwolffe/lanes/fg02c/mac-pre-cadence-fix-pty.log, mac-pre-cadence-fix-pty.exit and mac-pre-cadence-fix-storm/. Final Mac terminal rerun is **exit 0**, all seven named rows green at corrected cadence fixture 758e4ee against that identical production binary, after a **12.484 GiB** memory check. The all-book event row checks 408 keys; all eight long-walk cases have 160/160 aligned carrying frames, frame p99/max 1/1, wall p99 at most **33.818 ms**, worst **34.005 ms**. The storm observes forty distinct expected transitions, forty recorded sharp keys, at most one real afplay child, **50.671 ms p99**, zero extra cells. Silent failing players leave zero changed glyphs/styles and no live child.

Final terminal log/status: /Users/mfwolffe/lanes/fg02c/mac-final-pty.log and mac-final-pty.exit (0); source marker mac-final-pty.head. Build marker/log/status mac-play-build.head, mac-play-build.log and mac-play-build.exit (0). The complete captures and production binary now live in /Users/mfwolffe/lanes/fg02c/mac-final-target/, the complete archive pair in mac-toolchain/. All three exact clean Mac worktrees were removed without force after preserving artifacts. No Mac job remains.

Play (sound enabled): `/Users/mfwolffe/lanes/fg02c/fugue-play-d1d21fe --book 5 --size 120x40 --no-title`.

## Done-when

- [x] Exact-command pty reproduction and all fifteen preset counts before the fix.
- [x] One-event navigation, no cursor offset, selected rest/tie behavior and undo.
- [x] All-book developmental frame/edit census, release actual-input row and fresh species recordings.
- [x] Both named local plant assertions; docs, README and golden path-set audit.
- [ ] Exact-head full Linux gate complete (durable job above).
- [x] Single Mac release build, identical final production source tree and green final-fixture terminal interaction.
- [x] One immediate CI read and one audit recorded below; both were at the preceding head and are not final-head evidence.
- [ ] Coordinator reruns the audit at 7369f61 after the post-audit harness corrections; lane did not violate the once-only audit/read instruction.
- [ ] Coordinator watches PR-tier CI, retires the two plant drafts without merge, materialises this record and merges only on green.

The immediate, one-time CI read at 758e4ee found run **40448261014**, queued: https://github.com/wolffe-lang/fugue/actions/runs/40448261014. It was not polled or waited on. That head was superseded by the later offline-watchdog correction, so this run is **not final-head merge evidence**; no second CI listing was performed. The coordinator owns discovering/watching the PR tier at final head 7369f617a8abce673e1c8e425914a8cc13be94ba. PR #30.

The required audit ran exactly once from /Users/mfwolffe/GithubOrgs/wolffe-lang, with `bash wolf/tools/lane-audit.sh fugue fg02c 30 /Users/mfwolffe/lanes/fg02c/fugue`. Direct exit **1**, exact last line **AUDIT FAIL (footprint: module)**. Raw log/status: /Users/mfwolffe/lanes/fg02c/audit.log and audit.exit. At audited head 758e4ee, only in-progress CI/no completed green tier failed; ancestry, attribution, module paths, PR head, five sections, all 18 cited commits, removed worktree and orphan checks passed. The offline-watchdog and terminal-sampling corrections were discovered after this audit. Therefore it is explicitly a **prior-head audit**, not a claimed final-head audit, and the coordinator must audit 7369f61 before merge. No second audit was run.

No issue filed or closed. No physical speaker/font judgement is claimed by pty or PCM checks. No CI label or wait.

