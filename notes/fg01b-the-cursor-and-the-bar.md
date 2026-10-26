# fg01b — the cursor and the bar

_Materialised from fugue#23's PR body at the merge (048b0a8d); the lane's wrapper could not write Markdown notes._

# fg01b — the cursor and the bar

Head: `048b0a8dd45e744471e5a506e6feda12574e017d`.
The wrapper prohibits Markdown report files. This body is the full five-section note for the coordinator to materialise as `notes/fg01b-the-cursor-and-the-bar.md` on trunk.

## Prediction

Committed before implementation in `bd2d5b5` (`notes/fg01b-prediction.txt`): the panel uses cursor time (`onset + within`) but the rhythmic staff caret uses only the event index. A held event therefore hides valid moves. Sound, escape timeout and output buffering were not expected to cause this panel/caret split.

Confirmed on the maintainer's unchanged Mac `fugue-play-3ff811e8`, and the old game source built in the Linux CI container. Each panel update arrived on the first carrying frame; the caret changed on only 4 of 22 presses in every case. Left/Right updates `s.within` in `session.step`, while old `notation.frame` drew `^` at `event_column` without `s.within`. This is spatial quantisation, not a slow input queue: pausing does not repair it; the next event boundary finally changes the cell. No engine change is needed. The whole-page traversal below specifically measures the periodic stalls inside long held notes, not only median input latency.

The fix reserves at least one cell per editable time unit in each content-sized event, and draws the caret at that event's column plus the within-event offset. Heads still identify the note being edited. A compact grand staff uses the bar-number row for the caret when the lower rows are occupied. Two-digit bar numbers leave that cell clear. Playback still follows the sounding event and does not reuse the editing offset. No timeout, clock or redraw timer was changed.

A second, separately witnessed defect was the unconditional `sound: note-bank render_us ...` stderr line in Books I–V. Changing page after terminal entry leaked that text into the drawing when stderr shared the terminal; the earlier pty harness piped it away. The new merged-stderr row was red, then green after making that line use the existing `FUGUE_AUDIO_TRACE` guard. Left/Right never enters audition/preparation; Up/Down selects a cached WAV and does not synthesize. A real 20-audition witness verifies exactly one initial bank render, unchanged note-bank mtimes, no whole render and all 20 output handoffs.

## Forbidden

Original game work only. No engine, pin, Book VI file, CI workflow or shared engine tooling change. The common panel API is game code, not an engine change. `tools/cursor-check.py` is a game-specific pty witness loaded through the existing `tests/pty_rows.py` seam; this remains a module footprint.

No package installation, attribution trailer, issue action, label, merge, tag, release, planning-repo edit or memory edit. Linux gates use hasu's existing `localhost/pack-ci:fbee7e864f7dbee6` image (the exact CI Containerfile digest), block B under `flock`, `taskset -c 6-11` inside, and `--memory 12g`. Mac tests and the initial release build and its explicitly authorised final-head replacement use the lane's HOME/TMPDIR behind a scripted 8 GiB free+inactive gate. Scratch and worktrees stay under `~/lanes/fg01b/`.

## Inputs verified

- The contract, RULES sections 1–10, fg01a/fg01's records, README and player/design docs, and the input → session → manuscript → notation/staff → diff/write path.
- Unchanged lair `57870143ebbb4806b8bee40379e8c6e781f50842`; wolf 0.2.35, lupin 0.1.56, std `2386522eb059cca5a84108562c2c0a0e72345d34`. Full archive pairs fetched by pinned digest; release asset digests and installed pair/runtime hashes read twice (`notes/fg01b-evidence/toolchain-read-twice.txt`).
- R-fg01b-1: recommend **A**, implemented. The live panel includes only active-bar findings, with the bar still named on each finding row, including the selected-event rows. A clean bar says `No break in this bar`. Enter's verdict, hard-break total, stars and all-bar critic list remain global. B would add one dim `n more in other bars` line; it is not implemented, matching the request.
- README read against the final change, refreshed in the README-only commits `6e12c20` and `60a1249`: 132 checked tests and the new caret/panel behavior. The width trade-off is explicit: the mixed 120-column fixture now shows one, not two, quarters of bar 7 after six complete bars; 80 still shows three quarters of bar 3 after two complete bars. The whole-note caret needs eight cells rather than six.

### Shared panel API for fg02

The source-compatible `staff.panel(mut g, s, margin, t)` constructs Books I–V data and delegates to the common `staff.panel_data(mut g: grid.Grid, data: PanelData, margin: int, t: int)`. `PanelFinding { bar: int, rule: str }`; `PanelData { bar: int, beat: int, interval: str, consonance: int, pitch: str, figure: str, strong: bool, allowed: bool, local: List[PanelFinding], findings: List[PanelFinding], notice: str }`. Bar and eighth-beat are one-based; consonance uses existing 0/1/2 roles. The renderer owns the active-bar filter for both finding lists, row labels and layout. Book VI can supply its moving voice without a session/judge dependency. Names and fields were sent to the coordinator before completion. Extraction leaves all prior text/style goldens unchanged.

## Evidence index

Implementation and witnesses:
- `bd2d5b5` prediction; `ee76601`, `44aea7c`, `7509efe` named pty and bounded checked witnesses.
- `685826f` time-aware caret and width; `8d2725f` active-bar panel; `bb0494d` header spacing and two finding-bearing bar fixtures.
- `aff46ff` player docs; `08308e5`, `f43b3a4`, `744a579`, `fdb0978`, `6f01b6e` grouped text/style golden refreshes; `6e12c20` README; `d45a9c6` retained baseline, fixed Linux and plant evidence.

### Latency before and after

The row sends one Right, one Left, ten Rights at 30 Hz and ten Lefts at 30 Hz: 22 recorded presses per case. Both hosts give the following identical results. `P/C` means panel/caret frames from a press to its visible response. The first carrying frame is frame 1; all first-frame carets after the fix are also checked against independently computed expected columns, not just for any movement.

| Size | Tier | Sound | Before P | Before C | After P/C | Lost keys |
|---|---|---|---|---|---|---|
| 80x24 | rich | on | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 80x24 | rich | mute | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 80x24 | plain | on | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 80x24 | plain | mute | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 120x40 | rich | on | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 120x40 | rich | mute | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 120x40 | plain | on | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |
| 120x40 | plain | mute | 1, 22/22 | 1 for 4/22; stale for 18/22 | 1/1, 22/22 | 0 |

Before: neither single press moved the caret, even across the six idle ticks before the next press. Each ten-key burst had only two visible caret updates. Across the full scripted sequence the next observed cell change took 1–16 ticks, or never occurred before quit; that later change usually described a subsequent event boundary, not the earlier requested beat. `next_visible_cursor_update_after_frames` in the baseline journals records that distinction rather than inventing a timeout-based latency. After: both singles and all ten members of either burst align in the first frame; both bursts end at the panel's location in that frame, and the full sequence returns to time zero. Every case records all 22 keys in order.

Committed per-press journals: `notes/fg01b-evidence/{mac-before,linux-before,linux-after-release}.json`. Raw baseline traces/captures remain under `/Users/mfwolffe/lanes/fg01b/mac-long-before-captures/` and the Linux lane's `target/before-evidence/` directories. Final-head Mac and Linux journals/logs are at the durable paths below.

### Long-run worst-press measurements

Four complete out-and-back traversals of all 80 eighth positions produce 632 presses per case at 30 Hz, crossing every bar, whole note and scroll boundary. The row records every press, actual carrying frame, independently expected caret column and wall time from pty write to frame receipt. It checks p99 <=70 ms and max <=100 ms, so an isolated stall cannot hide behind the median. Raw per-press journals and traces are retained at the durable lane paths; summaries below omit no case.

Every baseline case: next visible caret change p99/max **14/15 ticks**, with **3/632 presses** still having no later cell change before quit. This measures the periodic stuck-cell symptom; a later cell change is not evidence that the earlier requested beat was ever drawn. Every final case: the first carrying frame matches both the panel and the independently expected caret column, p99/max **1/1 frame**, with all 632 keys recorded and final time zero.

| Host | Size / tier / sound | Correct-frame p99/max | Correct-frame wall p99/max, ms |
|---|---|---|---|
| mac | 80x24-rich-sound | 1/1 | 30.417/30.503 |
| mac | 80x24-rich-mute | 1/1 | 3.894/4.067 |
| mac | 80x24-plain-sound | 1/1 | 28.484/28.673 |
| mac | 80x24-plain-mute | 1/1 | 3.951/4.204 |
| mac | 120x40-rich-sound | 1/1 | 6.156/6.340 |
| mac | 120x40-rich-mute | 1/1 | 3.964/4.072 |
| mac | 120x40-plain-sound | 1/1 | 33.820/33.973 |
| mac | 120x40-plain-mute | 1/1 | 6.534/6.589 |
| linux | 80x24-rich-sound | 1/1 | 22.594/22.850 |
| linux | 80x24-rich-mute | 1/1 | 3.701/4.005 |
| linux | 80x24-plain-sound | 1/1 | 25.060/25.676 |
| linux | 80x24-plain-mute | 1/1 | 4.602/4.662 |
| linux | 120x40-rich-sound | 1/1 | 23.755/23.967 |
| linux | 120x40-rich-mute | 1/1 | 5.014/6.871 |
| linux | 120x40-plain-sound | 1/1 | 24.792/26.132 |
| linux | 120x40-plain-mute | 1/1 | 4.764/5.376 |

At the exact 30 Hz boundary, one Mac 120x40 plain/sound run coalesced 210 recorded keys into 105 two-key frames (the other 422 keys were single-key frames). No key was lost: panel and caret showed the correct final batch state in the same first carrying frame. Intermediate positions in a batch are not claimed as separately drawn. The raw `next_visible_change_frames` diagnostic compares successive per-key entries, so its duplicate entries for a shared frame are not used as an after-fix latency statistic. Correct-state frame latency and actual wall latency above remain checked for every record.

Raw journals: `/Users/mfwolffe/lanes/fg01b/{mac,linux}-long-{before,after}.json`; final Mac traces/captures `/Users/mfwolffe/lanes/fg01b/mac-final-target/pty/cursor-long/`; final Linux `/home/mfwolffe/lanes/fg01b/fugue/target/pty/cursor-long/`. The committed old-code summary is `notes/fg01b-evidence/long-before-summary.json`.

### Tests, goldens and plants

- The named `cursor-same-frame` pty row was red on the old binary on both hosts (exit 1), then green after the fix. It captures real terminal bytes and frame ticks, replays bytes through `--apply`, and accounts for actual recorded keys. Every successful final row checks both movement and column alignment.
- Checked tests cover single held-event movement in all size/tier combinations, room for every subdivision, compact grand-system visibility, active-bar findings in Books I–V, clean-bar behavior, and the critic's unchanged rendered global count. The 132-test suite has no rejected, unsupported or skipped rows. The added direct `PanelData` test verifies that an external moving-voice status uses the exact same active-bar filter.
- `active-bar-{80,120}` text and style goldens show findings in bars 2 and 3, with the cursor in each, then the global card. Golden path sets: zero prior paths removed, 32 new paths added. Existing native/release goldens, real recordings, restoration, gameplay, pitch census and exact Book I PCM gates remain included.
- Plant draft #21, `af32a86`: actual live cursor cells drawn from a saved pre-move state while the panel uses current state. Local `cursor-same-frame` exits 1 in all eight cases, including `panel=True, caret moved=False, aligned=False` on the first press. Later stale-but-moving cells also fail alignment. Evidence `notes/fg01b-evidence/plant-pre-move.txt`; original `/home/mfwolffe/lanes/fg01b/plant-pre-move/plant-red.log` and `plant-red.exit`.
- Plant draft #22, `05c07bb`: remove the bar predicate. `test_diagnostics_only_show_the_active_bar_book_1` through `_book_5` each fail by name; 126 pass, 5 fail, 0 rejected, 0 unsupported, exit 1. Evidence `notes/fg01b-evidence/plant-all-bars.txt`; original `/home/mfwolffe/lanes/fg01b/plant-all-bars/plant-red.log` and `plant-red.exit`.

The fixed commits preceded both plants. These are module-local planted reds under RULES section 7; no CI run was dispatched or waited on for them. Drafts remain unmerged for the coordinator to retire manually.

### Final-head gates and play

Exact-final-head Linux gate at `048b0a8dd45e744471e5a506e6feda12574e017d`: **exit 0**. `tools/check-linux` (fmt, 132 checked tests, both builds, selftest, both-backend goldens, all pty rows including the new long run, gameplay, pitch/PCM census), followed by native `cursor-same-frame`, `quiet-audio-page-change`, `cached-arrow-auditions`, and `tools/check-perf`, all green. Zero rejected/unsupported/skipped unit rows.

Durable Linux evidence: `/home/mfwolffe/lanes/fg01b/final-v2-gate.head`, `/home/mfwolffe/lanes/fg01b/final-v2-gate.log`, `/home/mfwolffe/lanes/fg01b/final-v2-gate.exit` (0), `/home/mfwolffe/lanes/fg01b/fugue/target/final-long-release.json`. The gate ran in the CI image under the required block-B flock and 12 GiB limit. No local job remains running. The earlier full gate at `6e12c20` was also green but is not substituted for this exact-head run.

Final Mac pty rows at that same head: `cursor-same-frame`, `cursor-long`, `quiet-audio-page-change`, `cached-arrow-auditions`, `panel-right-twice`, `selected-event-status`, and `book-5-rhythm-edits`, **exit 0**.

Mac play command (sound enabled):

```
/Users/mfwolffe/lanes/fg01b/fugue-play-048b0a8d --book 5 --size 120x40 --no-title
```

Mac binary SHA256: `aca378dc0d94263c4977ba3d07bfa86d620c8114b1b111d836a3d55091a2aa21`. Build gate **10.49 GiB** free+inactive; final pty gate **13.79 GiB**. Build log/exit `/Users/mfwolffe/lanes/fg01b/mac-replacement-build.{log,exit}`; final interaction log/exit `/Users/mfwolffe/lanes/fg01b/mac-final-pty.{log,exit}` (both exit 0).

The earlier `/Users/mfwolffe/lanes/fg01b/fugue-play-d45a9c69` remains intact but is **superseded**. It was built before the coordinator's later shared-API/audio/long-run requests; the coordinator explicitly authorised one replacement build, with the same unchanged 8 GiB gate. No further Mac build is claimed.

The two clean Mac plant worktrees were removed individually. After all Mac tests, the clean main Mac worktree was removed without force; target/pty evidence was preserved as `/Users/mfwolffe/lanes/fg01b/mac-final-target/pty/` and the verified archive pair as `/Users/mfwolffe/lanes/fg01b/mac-toolchain/`. Both play binaries and all durable logs/journals remain outside the removed tree. Linux worktrees and their evidence remain available.

Follow-ons: no engine fix or new game issue is established. Physical speaker/font play is not claimed by the pty. An unrelated pre-existing documentation discrepancy remains in `docs/PALETTE.md`: it still calls the cantus ink 130/plain 1 and describes its old contrast gate, while the implemented palette is 52/plain 9 and the existing staff gate requires the newer contrast. This pass did not rewrite that unrelated palette document; the coordinator may file it. No issue was filed or closed.

### Later requested implementation chunks

- `50c5038` supplied panel data and direct renderer test; `0e74ecd` merged-stderr red/green and cached-audition witness.
- `4626271`, `1be4258` long whole-page traversal, p99/max capture and explicit stall budgets; `72b3403` API/audio documentation; `60a1249` README count of 132.

## Done-when

- [x] Cursor and panel agree on every measured press; no timeout/timer change or lost press.
- [x] Active-bar diagnostics; global Enter verdict/counts unchanged; R-fg01b-1 A recommended and implemented.
- [x] Tests first, named old-code reds, both plants red locally, text/style goldens and README refreshed.
- [x] Explicitly authorised replacement final-head Mac play build and measured pty interaction, Linux gauntlet at the final head; no Book VI/engine/CI/pin changes.
- [ ] Coordinator watches the PR tier, merges only after green, accepts physical play, retires the two plant drafts unmerged and materialises this note.

PR **#23**, final head **`048b0a8dd45e744471e5a506e6feda12574e017d`**. The immediate one-time CI listing returned `[]`; it was not polled. The required audit then independently found CI run **[40413865254](https://github.com/wolffe-lang/fugue/actions/runs/40413865254)** in progress at this head. No label or CI wait was performed.

The required audit ran exactly once from `/Users/mfwolffe/GithubOrgs/wolffe-lang`:

```
bash wolf/tools/lane-audit.sh fugue fg01b 23 /Users/mfwolffe/lanes/fg01b/fugue
```

Direct exit **1**; exact last line **`AUDIT FAIL (footprint: module)`**. The only FAILs are the in-progress run and absence of a completed green tier at that head. Ancestry, attribution, module paths, PR head, all five sections, all 22 cited shas, removed worktree and orphan checks pass. Two conservative warnings treated the planned retirement of draft PRs #21/#22 as issue-closure language; they are plant drafts, not issue fixes, and remain for manual retirement without merge. This note now avoids that ambiguous phrasing. No issue was filed or closed. Audit log/status `/Users/mfwolffe/lanes/fg01b/audit.{log,exit}`. The coordinator owns discovery/watching of the PR tier and merges only on green.

