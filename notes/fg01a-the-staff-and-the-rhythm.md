# fg01a — the staff and the rhythm

_Materialised from wolffe-lang/fugue#19 (fg01a, head `3ff811e8`) by the orchestrator on 2026-10-26; the lane's wrapper refuses Markdown report files._

# fg01a — the staff and the rhythm

Footprint: cross-cutting

Final head: `3ff811e839248054d40eebb49418116d7234b212`.
The wrapper prohibits Markdown report files. This PR body is the complete five-section note for the coordinator to materialise as `notes/fg01a-the-staff-and-the-rhythm.md` on trunk.

## Prediction

Committed before implementation in `7173154` (`notes/fg01a-prediction.txt`): the staff lines, not interval arithmetic or sound, were wrong; the modal register clamp stopped lower edits; content widths would fit three complete bars plus part of a fourth at 80 and six plus part of a seventh at 120; at least one lower page would need more than three ledgers.

The first and last diagnoses held. `viewport.line = base + 2` made every line travel with the viewport. The old row and margin name agreed with each other, but not with a real clef: a nominal treble line could be the wrong pitch. Both old interval sites called `theory.interval` on the score pitches, and the part text used those same spelled pitches. No interval or audio pitch mismatch was found. The unchanged exact Book I PCM digest and the new independent fundamental estimates support that distinction; this is not a claim that the old staff was conventional.

The new mixed-value witness fits **two complete bars plus three of bar 3's four quarters at 80**, and **six complete bars plus two of bar 7's four quarters at 120**. The 80-column prediction missed. The initial, unedited Book V preset fits four complete bars at 80 and seven at 120; the mixed witness deliberately adds subdivisions and a compound interval so both sizes exercise a partial bar.

## Forbidden

Original drawing, rules, tests and prose; no engine or pin change, third-party source, package installation, planning/memory/configuration edit, attribution trailer, label, merge, tag, release or issue action. No fg02 branch or Book VI content/judge file touched. No process killed.

Linux builds, tests and perf ran in the pinned lair container on kasumi CPUs 0–3 under `/home/mfwolffe/lanes/kasumi-cores-0-3.lock`, released between gates. The Mac ran **one** final-head release play build after its scripted 8-GiB gate; no Mac test or golden loop. The three negative drafts were opened only after the fixed parent was committed; each run was listed once, without waiting or labelling.

## Inputs verified

- Base `39464a1`, following fg01 `d3e3f7db`; the full contract and subsequent panel/Book-VI errata, both prior notes, campaign, RULES §1–§10, named docs/modules and Wolf guide were read.
- Unchanged lair `57870143ebbb4806b8bee40379e8c6e781f50842`, wolf 0.2.35, lupin 0.1.56, bundled std `2386522eb059cca5a84108562c2c0a0e72345d34`. Whole Linux and Mac archive pairs verified by digest; release asset digests, stamps, identities and binary/runtime hashes read twice in `notes/fg01a-evidence/pins-read-twice.txt`.
- README read and refreshed in README-only commits; Sound's former fifteen-note-bank claim was corrected too.

### Recommendations implemented, not rulings invented

- **R-fg01a-1 A/B:** choose treble when the initial lowest voice pitch is at or above G3, bass otherwise. Fixed treble E4 G4 B4 D5 F5 and bass G2 B2 D3 F3 A3; accidentals share their letter's row. The census found **Book I seed 7** would need **four ledgers above bass**. Following the contract's B threshold and coordinator relay, that page uses **treble over bass**, each voice on its own page-selected clef, with the shared middle-C ledger. At 80x24 the grand system spends the title/header space on 21 pitch rows, intervals on row 22 and the hint on row 23. All other sampled starting pages fit at most three ledgers. On seed 7's grand system each voice fits without a ledger. Book VI's generated-subject census belongs to fg02 after integration; it is not fabricated here.
- **R-fg01a-2 A:** `[` split, `]` join, `.` dot, `t` outgoing tie, `r` rest/back. All preserve duration where required, undo completely and use the unchanged species classifier/judge. II–IV retain their species rhythm, including the prior opening-rest and IV incoming-tie conventions.
- **R-fg01a-3 editor extent:** remove `session.step`'s modal `bottom` / `bottom + 14` clamp (above: `28 + mode`; below: `21 + mode` in I, `20 + mode` later). Recommend the page-owned inclusive `range_low`/`range_high`, C1–B6 for I–V, with the audition bank prepared over the same range. Species legality remains a judge finding, not a silent register lock. Book VI may set C3–C7 before preparation.
- **R-fg01a-4 dot convention:** add half the selected quarter/half's duration by borrowing from the following event in the same bar; consume it if exhausted, otherwise require a valid remaining value. Refuse by name instead of changing the bar's sum. Integer-eighth values are 1/2/3/4/6/8; 3 and 6 are dotted values.

### Drawing, pitch and selected-event status

- Staff/head API shape is preserved. `staff.system(state, view)` owns one/two-staff configuration; `head` still takes the existing cantus flag and returns the true row. `label_row` is fg02's entry-label seam; `interval_row` follows the lowest note, ledger, staff or tie in each column. The viewport scrolls without changing any line's pitch.
- The independent proof covers **1,254 initial/reference note rows on 30 pages**, all fifteen presets plus seeds 0/7/11 per book, and **24 distinct synthesized fundamentals**, including cadence sharps. Every FFT estimate is within **1%** of its spelled pitch. The peak search is not centred on the expected frequency. Both compiled backends pass. `staff.interval_at` is held against `theory.interval` on the same pitches, not a drawn row.
- Cantus is unchanged hollow `○`/`o`, **bold rich index 52 (#5f0000)**, plain **bright red 9**. Player is rich 24/plain 4. Measured rich contrast: **13.815:1 on 230**, **10.488:1 on 223**, **10.307:1 on 222**. No theme-independent plain RGB claim.
- Content width is **one barline + sum(max(value minimum, pitch-name bytes + 1, interval-label bytes + 1))**. Tuned minima: **whole 6, half 5, quarter 4, eighth 4** (dotted half 5, dotted quarter 4). Four cells accommodate an eighth flag, ledger and complete label. Left boundary 7, first head 9, critic margin `columns - 24`, right boundary `columns - 26`; an event fits only while `x + width - 2 < columns - 27`. Every drawn partial bar is numbered and marked `>>`; scrolling keeps the complete selected event visible.
- **6b:** fg00a fixed the heading, not the status content's source. The status now follows cursor time: **Bar N, beat B:8**, interval/class, figure and selected-event local findings. `species.event_breaks` retains only findings emitted at that event by the same vertical/motion rule pass; it cannot borrow a neighbour's finding in the same bar. The separately titled **Breaks: whole page** list includes whole-line melodic findings and their bar locations. A pty row checks five distinct selected intervals across two bars, and a checked regression distinguishes two events in one bar.
- Book VI seams: page-owned range and `rhythm_editable`; `editor_unit` is eighths for editable rhythm, otherwise the shortest written value. `#` cycles natural/sharp/flat away from the cadence only when book == 6; earlier guards stay. Spelled accidentals reach head/judge/audio. Replay IDs 1–25 unchanged, 26/27 reserved for book-6/voice-switch, dot appended at 28. No mistaken F→F-sharp transposition example was introduced.

## Evidence index

Implementation chunks:
- `7173154` prediction; `aac4e3a` fixed clefs; `1e16aea` lower editing extent.
- `59f981e` initial pitch proof; `a1b8c5c` cantus ink; `5c9a6dc` content layout/grand system.
- `f75eb91` reversible rhythm and page capability; `c220e89` reflow/status; `7380e50` stable Book VI seam.
- `7c9c77b` terminal witnesses; `f3c854f` goldens; `589f472` player docs; `9906a81` exact partial-fit witness.
- `ea248ec` README; `385e5b4` complete preset reference/accidental PCM proof.
- `3d5f4e5` exact event-local findings; `00b3ec2` final critic/clef goldens; `bc5b34a` README coverage refresh.
- `3ff811e` raw gate, plant and pin evidence.

Tests:
- [x] Canonical format; **120 checked tests**, zero failed/rejected/unsupported/SKIP.
- [x] Native/release builds, decoder/diff selftest, both-tier goldens on both backends.
- [x] **21 pty rows**, including three-ledgers-below-and-back, selected-event-status and Book V live rhythm editing/replay verdict.
- [x] 300-line Book I census; 48 certified later-book seeds; fifteen three-star references; score-tampering refusals and actual solved recordings.
- [x] 127 species verdict rows, classifier witnesses, exact two-voice PCM and independent fundamental proof on both backends.
- [x] Perf: 300 idle voluntary context switches / 10 seconds; input median/p90 **32.2/32.3 ms**. Rich/plain 120x40 frame means: I **88/74 us**, II **251/242**, III **420/408**, IV **256/245**, V **273/262** (all means below 500 us; III maximum 830/709 us).
- [x] Full Linux gate rerun after all plants at exact final head **3ff811e839248054d40eebb49418116d7234b212**, direct exit **0**, clean tracked tree. Remote staged-tree hash was matched to the final bundle before moving the branch. `/home/mfwolffe/lanes/fg01a/final-head-linux.log` and `.exit`, mirrored under `/Users/mfwolffe/lanes/fg01a/`.
- [x] One final-head Mac release build, direct exit **0**; memory gate passed **40,031,158,272 bytes** against **8,589,934,592**. No Mac test or physical-listening claim.

Raw committed evidence is under `notes/fg01a-evidence/`; the final-head rerun and Mac build logs remain outside the repository to avoid moving the already-tested head. The old staff's frame is `before-staff-80-rich.txt`; compare the new `tests/goldens/staff-80-rich/frame-0000.txt`. The exact Book I PCM digest is unchanged.

Golden inventory: **107 directories**, **101 changed/added**. Changed families: `art`; rich/plain 80/120 pairs for `staff`, `critic`, `hear`, `walk`, presets 1–3; all Book II–V preset/seed families plus Book V eighths; new `cursor-1`, `cursor-3`, `ledger`, `partial`, `rhythm-edit` pairs at both sizes. `audio`, `verdicts` and four title directories are unchanged. Exact paths are in `notes/fg01a-evidence/golden-paths.txt`.

### Negative drafts

All fixed code preceded the plants. Local reds were named assertion failures, direct exit 1, with no compile rejection. Their immediate one-time run listings returned `[]`; the coordinator owns run discovery/watch, not this lane.

| draft | full head | expected Linux red |
|---|---|---|
| #16 clef | `2fc00aa717010492061e267ff3df9f31b1b248a0` | `test_treble_second_line_is_G4_and_bass_top_is_A3` (also the margin round-trip) |
| #17 interval | `2bf498fc90ab5aee073284d7f50f2bd4b9a5bc7b` | `test_interval_label_uses_pitch_not_row` |
| #18 split | `d98ad33f842bb81fa1a14c50519bca767685d31e` | `test_split_preserves_every_bar_sum` (also rhythmic edit/partial tests) |

### Play and follow-ons

Mac binary **`/Users/mfwolffe/lanes/fg01a/fugue/target/fugue`**, SHA256 **`075940e2472d8e2e3f4a4f1206b1cb6fb6c109621d5e6d937b070b94183f6d9a`**. Play florid with `--book 5 --size 120x40 --no-title`; use `--seed 7 --size 80x24 --no-title` for the grand-staff case, or `--plain`. No flags opens the book desk. Do not pass `--mute` when listening. Build log/status `/Users/mfwolffe/lanes/fg01a/mac-play-build.log` and `.exit`.

No new engine issue is established. Existing engine decoder/output-owner follow-ons remain unchanged. fg02 must rebase and measure its generated three-voice pages, use the page range before preparing its audio bank, and keep its fixed answer versus editable countersubject flag. No issue was filed or closed, and no planning or memory file was edited.

## Done-when

- [x] Fixed clefs, range-selected grand system, lower ledgers, independently proved pitch truth, stronger cantus ink, partial measures and reflowing interval rows.
- [x] Cursor-local status content, live rhythm keys, undo/rejudge, tests, goldens, docs and three negative draft PRs.
- [x] Exact-final-head Linux gate and one memory-gated Mac play build; README current.
- [ ] Coordinator discovers/watches the plant CI reds and closes drafts unmerged; labels this final head for full tier, watches it, accepts physical play and materialises this note before merge.
- [ ] One immediate main-run read and the required final audit are appended below; this lane never waits on CI or labels.

### Final-head hand-back and audit

PR **#19**, head **3ff811e839248054d40eebb49418116d7234b212**. The immediate one-time main-run listing returned `[]`. The required audit independently identified **[40373362572](https://github.com/wolffe-lang/fugue/actions/runs/40373362572)**, in progress at that exact head. No run was polled or waited on.

The required audit ran once from `/Users/mfwolffe/GithubOrgs/wolffe-lang`:

```
bash wolf/tools/lane-audit.sh fugue fg01a 19 /Users/mfwolffe/lanes/fg01a/fugue
```

Direct exit **1**; exact last line **`AUDIT FAIL (footprint: cross-cutting)`**. Failures are only the unfinished head run/no completed green tier, the coordinator-owned full-matrix label not yet applied, and the intentionally retained Mac play worktree. Ancestry, attribution, footprint, PR head, all five sections, all twenty cited shas and orphan checks pass. `/Users/mfwolffe/lanes/fg01a/audit.log` and `.exit` retain the result. The checklist's immediate-read/audit item is now complete.

Pruned only these exact lane-owned paths after the final gates:

- Three clean Mac plant worktrees, removed individually without force: `/Users/mfwolffe/lanes/fg01a/plant-clef`, `/Users/mfwolffe/lanes/fg01a/plant-interval`, `/Users/mfwolffe/lanes/fg01a/plant-split`.
- Under `/home/mfwolffe/lanes/fg01a/fugue/`: `target/native`, `target/release`, `target/goldens`, `target/gameplay`, `target/species-gameplay`, `target/staff-check`, `target/pitch-proof`, `target/look-five`, `target/look-grand`, `src/.lu-cache`, `tests/__pycache__`. An accidentally misplaced lane-only `src/studies.lu` copy was removed immediately after its named duplicate-entry refusal, before the successful complete proof; the real `src/studies/studies.lu` remains.
- Under `/Users/mfwolffe/lanes/fg01a/fugue/`: `target/release`, `target/fetch-tmp`, `src/.lu-cache`.

The Mac play binary was hashed again after pruning and is unchanged. Toolchain pairs, final Linux `target/fugue`, pty/audio captures, raw evidence and the Mac play worktree remain. No lane job is running. Exact prune lists are `/home/mfwolffe/lanes/fg01a/pruned.txt` and `/Users/mfwolffe/lanes/fg01a/pruned.txt`; the three explicit worktree removals are recorded here. No broad worktree loop, process-name kill or unrelated directory was touched.
