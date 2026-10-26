# fg00a — the staff proper (fugue#8, merged at 6061b528)

Materialised on trunk from the PR body by the orchestrator at the merge (a Codex lane writes no note file).

Footprint: cross-cutting

This body is the complete fg00a note for materialisation as `notes/fg00a-the-staff-proper.md`. The wrapper prohibits Markdown report files. Final head: `6061b528cb7e52b5caefb83d65c7bfb4213ae89f`.

## Prediction

Committed before implementation in `3edd682`: clipped fixed E4–F5 lines and overlapping ledgers would explain the disjoint staff; pitch arithmetic would round-trip; h appeared wired, requiring an actual output-owner witness; staff/preset/art goldens would move. These held. The critic cases also contain an initial staff frame, so their directories moved too. Title and verdict goldens did not move.

The old seed-7 viewport showed only three of the fixed five staff lines. Four-cell ledger runs overlapped across adjacent notes below them, resembling broken stacks. There were no musical bar lines, only the critic separator. Five lines now belong to the supplied viewport, with three-cell ledgers and permanent crossing boundaries. No underscore is drawn, including in the decorative study.

The selected-bar state was not stale in the baseline Linux pty: Right twice rendered Bar 3. A second, insufficiently distinguished Bar N was the first critic finding. The panel now begins with bold blue **Editing bar N**, above the separate **First break / at bar N**. A row-specific pty assertion checks Editing bar 3 after two Rights. The Up/Down witnesses check every boundary on every frame; no engine diff bug was reproduced.

## Forbidden

Original drawing, tests and prose; no engine change, third-party implementation, package installation, planning/memory/configuration edit, label, merge, release or attribution trailer. No process killed. The Mac is reserved for one final-head release play build under a scripted 8-GiB gate with three-minute retries, followed by one sound-on h lifecycle witness; no Mac golden generation or test loops. Linux work uses the pinned engine container, `LAIR_CPUS=0-3`, and the shared flock, releasing it between gauntlets. fg01's books, beats and ties are untouched.

## Inputs verified

- Base `8d411917e3812277375d7797e35cb65a6f8aaab4`; lair `57870143ebbb4806b8bee40379e8c6e781f50842` unchanged, read twice.
- Wolf 0.2.35 / lupin 0.1.56 / std `2386522eb059cca5a84108562c2c0a0e72345d34`; both host archive pairs verified by digest, independently read twice from release metadata in `notes/fg00a-evidence/pins-read-twice.txt`.
- Full contract and errata, fg00 note, all named docs and modules, staff goldens, engine grid/sound contracts, campaign, RULES §1–§10 and Wolf guide. The root fugue/lair worktrees were stale; origin/trunk/pinned docs were used.
- **fg00's note claims replay-audio evidence; the repo had no --sound-replay and no PCM golden; added here.** This is an evidence correction, not an engine change.
- R-fg00a-1 follows the maintainer's subsequent ruling: **retain hollow ○/o cantus and filled ●/* player heads, colour only, no halo**. Cantus rich 130 (saturated burnt orange), player 24 (dark blue), on parchment 230: contrasts **4.605:1 / 6.876:1**. On grain 223: **3.496:1 / 5.220:1**; on sounding 222: **3.436:1 / 5.130:1**. Plain red 1 versus blue 4 on 7 is theme-dependent; no RGB claim.
- Recommend and implement **R-fg00a-2 A**, not a ruling: named shared diatonic viewport. `test_pitch_row_margin_round_trip_whole_viewport` proves both directions, every margin name, C4, all line/space steps and ledger continuation across bases 21–35 on both tiers. No pitch-name arithmetic mismatch was found. The defect was clipping five fixed lines; before/after staff goldens show the changed layout. Bottom C4 reproduces exactly E4 G4 B4 D5 F5, with F4 A4 C5 E5 spaces. The spiral study is decorative, not a treble-clef promise.
- fg01 seam: `Viewport`, `viewport`, `row_of`, `pitch_of`, `lines`, `draw_staff`, `ledger`, `head`. Head placement returns the unclamped row and takes cantus/selected/lit flags. `session.ticks_per_whole`, `piece_ticks`, `event_at` and `ear.part(cantus, voice)` name the playback seams. Rhythm can replace event lookup and score emission without replacing audio ownership. See `docs/DESIGN.md`.
- README read and refreshed in its own commit: 71 tests, 13 pty rows, new PCM export and expanded witnesses.

## Evidence index

Implementation chunks:
- `3edd682` prediction.
- `c00511d` five lines, supplied viewport, mapping and colour tests.
- `acce80d` whole-piece output owner witness, PCM export and independent frame gate.
- `4b49f29` docs; `ec94c35` README-only refresh.
- `964749f` first-line editing panel and baseline evidence.
- `6ed104c` shared clock/event-list seams.
- `99ade62` both-tier walks, listening and staff goldens.
- `6061b52` named plant reds and measured evidence.

Linux gate at the exact final source tree, before evidence/docs-only final commit: `notes/fg00a-evidence/gauntlet-2.log`, direct exit 0. The post-plant rerun at the pushed final head is also green, as recorded below.

- [x] Canonical format, **71 checked tests**, zero failed/rejected/unsupported/SKIP.
- [x] Native and release builds, binary selftest, both-backend goldens, 300-line game census, three references, solved recording and score-tampering refusal.
- [x] **13 pty rows**, including row-specific Right twice and h render-to-output handoff.
- [x] Four size/tier combinations × **40 Up/Down frames**, every bar crossing present in every frame; five line runs checked before note/bar overlays, and final line rows checked for no gaps.
- [x] Four size/tier combinations × **11 listening frames**, both sounding heads lit at each bar, first through last, then extinguished.
- [x] Exact **10.000000-second / 1,920,000-byte PCM** seed-7 golden on both Linux backends and the actual h WAV. SHA256 `b558957b00de6c4b92494e872e088a9eb16aabf23a3a25bcff8e7d40738c17c6`.
- [x] Six-glyph inventory, plain ASCII and contrast assertions. Every audio bar has nonzero stereo energy, no clipped sample, L/R RMS ratio <2.
- [x] One final-head memory-gated Mac build and actual owned afplay lifecycle, detailed below.
- [ ] Physical listening/font judgement remains for the player; a process/PCM witness is not a human hearing claim.

Audio diagnosis: baseline Linux h was already dispatched to whole-1.wav, not merely the audition file. The old hint buried h among other keys; it now leads the permanent hint. The score retains organ p / choir mp (five dB favouring choir) with pans -25/+25. Measured initial-quarter RMS was 183.6 for the whole piece versus 91.8 for the audition (~6 dB louder), so a whole-piece level below audition was not reproduced. We do not invent a missing afplay call or claim subjective balance from PCM. The new independent Mac row must observe the actual whole-file child alive, then its exit and reap; the Linux sink alone is explicitly insufficient. The spare one-second render padding is removed; the cursor and phrase now both span ten seconds. Diagnostic per-cue logging is opt-in and stderr must be redirected outside a pty so it cannot move the draw pen.

Changed golden directories: `art`, new `audio`, and rich/plain pairs at 80/120 for `staff`, `critic`, `preset-1`, `preset-2`, `preset-3`, new `walk` and new `hear` (**30 directories moved/added**). Critic's initial staff frames change; its final cards do not. `title-*` and `verdicts` are unchanged.

### Negative drafts

Fixed code preceded all three plants. Each has canonical formatting and a genuine named local red, not a compile rejection. The immediate one-time CI listing returned `[]` for each; the coordinator owns run discovery and watching, not this lane.

| Draft | Head | Expected Linux red | Local result |
|---|---|---|---|
| #5 gap | `db6f45c08d9a6c6a62bb486f8ea244df13067570` | `test_five_staff_lines_are_unbroken_on_both_tiers` | 70 pass / 1 fail, exit 1 |
| #6 wrong margin | `bd4c29f99d0f29ee96a5dbcfa1f11ba69c11310e` | `test_pitch_row_margin_round_trip_whole_viewport` | 70 pass / 1 fail, exit 1 |
| #7 silent h | `2398553499e7b073109616167574098fa36e86bd` | `hear-whole-is-played`: h rendered but never handed whole WAV to output | exact WAV/PCM passes; handoff assertion fails, exit 1 |

Logs and statuses are under `notes/fg00a-evidence/plant-*`; draft publication and immediate run reads are in `plants-publish.log`.

### Play and follow-ons

Final Mac play binary: `/Users/mfwolffe/lanes/fg00a/fugue/target/fugue`. No flags opens the title/tutorial; `--seed 7 --size 120x40` opens a seeded page after the title, `--no-title` goes directly to its staff, `--plain` selects ASCII. Do not pass `--mute` for listening. Press h at the staff.

No new engine issue is established. The already-known nonblocking output-owner/cancellation seam and CSI-u decoder remain engine follow-ons; neither was patched privately. The coordinator must materialise this note on trunk and correct fg00's replay-audio overclaim. Mac lifecycle, final-head rerun, CI/audit and prune facts follow below.

## Done-when

- [x] Five solid named lines on both tiers; mappings proved, unchanged note symbols visible by colour, current bar and full-piece cursor/hint.
- [x] Original work, rhythm-facing seams, tests/goldens/docs and three draft plants with named local reds.
- [x] Final-head Linux rerun after the plants; one final-head Mac play proof.
- [ ] Coordinator obtains and watches plant CI reds, labels final head for full tier, watches both host legs, accepts play, closes plants unmerged and materialises this note.
- [x] Lane read the main run once and ran the required final audit once; no CI waiting or labelling.


### Final-head playback and local gate

At **6061b528cb7e52b5caefb83d65c7bfb4213ae89f**, the one Mac gate refused **1.699 GiB**, retried after three minutes, and proceeded at **11.881 GiB**, above the scripted 8-GiB floor. One release build and one `hear-whole-is-played` row ran; direct exit **0**. No other Mac build, test loop or golden generation ran.

- WAV: `/Users/mfwolffe/lanes/fg00a/fugue/target/pty/hear-whole/whole-1.wav`, **10.000000 seconds**.
- Owned `/usr/bin/afplay` **PID 31608**, game parent **31450**, observed alive with that exact WAV argument; then `player-end slot 0 status 0`, `ps` exit 1, owner reaped true. The next frame did not kill it; the row remained alive through the complete pass.
- Actual WAV PCM SHA256 **b558957b00de6c4b92494e872e088a9eb16aabf23a3a25bcff8e7d40738c17c6**, equal to both Linux backends' export and h output. The Mac proof checks the PCM inside its sole live h playback; it does not run a second offline render.
- Mac play binary `/Users/mfwolffe/lanes/fg00a/fugue/target/fugue`, SHA256 **c94cc60879c24fa273af0ff0da75b03fe2bc9e582543e437b6472b111c4fb78b**.
- Logs: `/Users/mfwolffe/lanes/fg00a/mac-final-play.log` and `.exit`. These show an actual player lifecycle, not a human listening judgement.
- Pushed-head Linux rerun after restoring every plant: direct exit **0**, clean tracked tree. `/home/mfwolffe/lanes/fg00a/final-head-linux.log` and `.exit`, mirrored at `/Users/mfwolffe/lanes/fg00a/final-head-linux.log` and `.exit`. Compiler and replay gates cover the final source, not an earlier build.

Pruned, only within fg00a: the three clean Mac plant worktrees `plant-gap`, `plant-margin`, `plant-silent` were removed individually without force. On kasumi, `/home/mfwolffe/lanes/fg00a/fugue/target/{native,release,goldens,gameplay,staff-check}`, `src/.lu-cache`, `.lu-cache`, and `tests/__pycache__` were removed. The diagnostic `tests/staff_probe.py` was removed before the final gate. The Linux `target/fugue`, WAV captures and toolchain remain; the Mac play worktree remains for play. No lane-owned process is left running.

PR #8's immediate one-time run listing returned `[]`. No CI wait, repeat query or label by this lane; the audit's independent required read is reported next.


### Audit and hand-back

The required audit ran once at the final head, direct exit **1**. Last line:
**`AUDIT FAIL (footprint: cross-cutting)`**.

It independently found PR-tier **40264973587 completed success**, every job/step/annotation clean, and full-tier **40265115869 running**. The coordinator had applied `full-matrix` by that read; this lane never labelled. The only failures are the still-unfinished full tier and the intentionally retained Mac play worktree. Ancestry, attribution, footprint, PR head, all five note sections, all nine cited commit shas and orphan checks pass. Log `/Users/mfwolffe/lanes/fg00a/audit.log`, status `/Users/mfwolffe/lanes/fg00a/audit.exit`.

The coordinator owns the full-tier watch and the three plant CI outcomes. No run was waited on by this lane. Keep the Mac binary/worktree for play, then materialise this PR note before merge.

