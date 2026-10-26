# fg00 — the staff (fugue#4, merged at 996754bf)

Materialised on trunk from the PR body by the orchestrator at the merge (a Codex lane writes no note file).

Footprint: cross-cutting

This body carries the complete fg00 note for materialisation as `notes/fg00-the-staff.md`; the agent wrapper prohibits Markdown report files. Final head: `996754bf3bef9df979370377ef9d5224ab0298a0`.

## Prediction

Committed before implementation in `77d2348`: 300/300 valid generated cantus firmi; approximately 60/30/10 percent with two/three/four leaps; at least one Fux oracle rejected; note-bank preparation under five seconds; 120x40 frame averages under 500 us; margin pitch names clearer than the drawn clef on plain.

Measured playable-generator census: **300/300 valid**, 50 per mode, all ten notes; **9 two-leap, 167 three-leap, 124 four-leap** lines. The leap-distribution prediction missed. The raw melodic-pool census is separately 15/165/120; gameplay additionally proves a legal counterpoint exists on the assigned side before offering the cantus. No three-star promise is made for every seed. The three tutorial references each earn three stars.

All six Fux lines have named breaks under the documented modern conventions; none is silently waived. Final-head note-bank preparation: **21,490 us** for the two-octave Dorian bank including its raised cadence note. Linux release render+diff at 120x40: **rich 71 us average / 138 max; plain 57 / 116**. The timing predictions held. Margin names remain the recommendation.

## Forbidden

Original game rules, critic prose, drawing, tutorials and reference solutions. Only trail's tooling/workflow scaffold and the pinned lair engine, including its binary selftest, were reused. The six Fux cantus firmi are cited historical test oracles only; no Fux counterpoint or other game code/assets/music enters gameplay.

No engine, planning-repo, configuration or memory edit; no package installation, label, merge, release, tag or issue action. No attribution trailers. No maintainer server touched. All tests, goldens, plants, census and performance ran in the engine container on kasumi CPUs 0–3 under `/home/mfwolffe/lanes/kasumi-cores-0-3.lock` with `LAIR_CPUS=0-3`. Signal witnesses are the engine pty rows using terminal bytes. No process was killed.

The Mac ran exactly one final-head release play build, with no tests or golden loops. Its scripted vm_stat gate first refused 4.881 GiB, retried three minutes later, and proceeded at 22.147 GiB against the 8 GiB floor. Whole compiler/runtime archive pairs were used on both hosts.

## Inputs verified

- Base `fec9f4d`; lair trunk **`57870143ebbb4806b8bee40379e8c6e781f50842`**, read twice and retained in `lair.pin`.
- Pinned wolf 0.2.35, lupin 0.1.56, bundled std `2386522eb059cca5a84108562c2c0a0e72345d34`; both host archive digests read twice from release metadata and independently checked by the fetchers. Evidence: `notes/fg00-evidence/toolchain-read-twice.txt`.
- Complete contract/campaign, trail note and scaffold tree, engine/replay/sound docs and mixer note, cub palette/glyph discipline, PAX part format, lane rules and Wolf guide. Local trail/lair checkouts were stale; fetched trunk versions were read instead.
- Fux, *Gradus ad Parnassum* (Vienna, 1725), original public-domain scan https://archive.org/details/gradusadparnassu00fuxj_0 : printed pages 47, 51, 52, 53, 55, 62; archive pages n60, n64, n65, n66, n68, n75. Cantus staves transcribed independently into `tests/oracles/fux.txt`, normalized only by whole octaves. The typed oracle is held to that transcription text.
- README read and refreshed in its own commit; it distinguishes playable Book I from planned later books and states the Linux WAV-sink boundary.

### Recommendations implemented, not rulings decided

- **R-FG-5 A:** pitch names. Compare `tests/goldens/art/names-80-plain.txt` with `clef-80-plain.txt`, and their rich/120-column companions. Names communicate absolute pitch; the plain drawn clef reads as a spiral. C4 is bold when in view.
- **R-FG-6/7/8 A:** arrow-based entry, legal/illegal followed by one-to-three stars, three tutorial pages followed by seeded pages and a UTC daily seed.
- **R-FG-9 A:** organ p for the cantus, choir mp for counterpoint. Prepared waveform/output evidence exists; physical listening judgement is still owed to play, not claimed by automated tests.
- **R-fg00-1 A:** define sequence as adjacent equal-length two/three-note blocks with identical diatonic interval patterns; define balance as rising/falling motion counts differing by at most three. These stricter, explicit conventions account for historical oracle rejections.
- **R-fg00-2 A:** bounded ten-note enumeration, 200,000-prefix ceiling, up to 64 candidates per mode, best-sixteen shape band. Climax placement and interval variety rank candidates; balance is a hard admission check. Cycle from the seeded index until an independent bounded search proves a legal answer on the requested side; discard that answer. This prevents valid-but-unsolvable exercises. Longer/less repetitive pools remain a future expansion, not a false uniqueness claim.
- **R-fg00-3 A:** one shared pitch-space staff with a viewport that fits both lines where possible and ^/v overflow marks otherwise. Fixed requested layout (80x24 default), no pitch compression or exercise mutation on terminal resize; resize recording is not implemented.
- **R-fg00-4 A:** use game-owned wolf-std afplay children with nonblocking polling because lair's Output only offers blocking finish. Synthesis, prepare and WAV encoding stay in lair. Linux keeps the same files as a WAV sink. Listening locks edits for the pass; quit restores the terminal before waiting for release tails. Up to 32 live cue owners; default temporary output rotates files.
- **R-fg00-5 A:** explicit style goals: contrary >=50%, steps >=60%, separate unique climax, parallel thirds/sixths at most three bars, interval variety >=3. Legal yields one star, at least three goals two, all five three. The three tutorials reuse one original contour in Ionian/Dorian/Mixolydian to isolate the changing cadence.

### Fux oracle verdicts

Numbers below are one-based bars; these exact findings are asserted, not merely printed.

| mode | expected named breaks |
|---|---|
| Dorian | sequence 3,5,7,8; balance 1 |
| Phrygian | sequence 3 |
| Lydian | successive-leaps 5,10; recovery 9; leap-count 1 |
| Mixolydian | recovery 6,9; successive-leaps 6,10; sequence 9; leap-count 1 |
| Aeolian | sequence 1,2,3,7,7,8,9 (bar 7 starts both a two- and a three-note repeated figure) |
| Ionian | sequence 9 |

## Evidence index

Implementation chunks:
- `77d2348` prediction; `78c65d4` pinned scaffold and five engine pty rows.
- `9d6ed8f` theory, named checks, enumeration, census and historical oracles.
- `6a8e168` manuscript, two-tier studies and reversible editor.
- `aa5dd7e` prepared note bank and two-voice audition.
- `0e3a512` first-species judge, tutorials, solved goldens and real recording.
- `aa02c8d` complete gates, replay audio, bounded ownership, verdict/glyph checks and editor edge cases.
- `8d91f05` player documentation; `78fd9e8` README-only refresh; `996754b` named plant logs and test-cache ignore.

Final-head Linux checkout was fetched and staged-tree-compared to `996754b`, then the complete gate and slack-1 performance ran with direct exit **0**, leaving the tracked tree clean. Logs: `/home/mfwolffe/lanes/fg00/final-linux.log` and `.exit`, mirrored at `/Users/mfwolffe/lanes/fg00/final-linux.log` and `.exit`. Earlier stage and plant logs are committed under `notes/fg00-evidence/`.

- [x] fmt, **65 tests**, zero failed/rejected/unsupported/SKIP.
- [x] Native and release builds and binary decoder/diff selftest.
- [x] Both-backend goldens and gameplay checks; **26 golden directories / 417 files**.
- [x] 300 raw melodic-census cases; 300 solution-certified game-census cases on each compiled backend.
- [x] Legal/illegal witness per hard rule, three three-star references, full verdict golden and score-tampering refusal.
- [x] Eleven pty rows: five engine rows plus editor/ear, title/staff/card quit, Escape and solved recording.
- [x] Actual `tests/replays/solved-80.pk` recomputes **three stars**, including title-start state; authored scripts are separately identified.
- [x] Original illuminated F; pitch-name/clef alternatives; note-light sequence; both tiers at both sizes; six non-ASCII glyphs checked both ways and plain restricted to ASCII.
- [x] Final-head Linux frame averages at 120x40 rich/plain **71/57 us**, maxima **138/116 us**; input median/p90 **30.7/31.7 ms**, repeated **31.7/32.3 ms**; 300–301 idle voluntary switches per ten seconds.
- [x] One final-head Mac release play build, direct exit 0; **no local Mac tests claimed**.
- [ ] macOS full-tier tests and physical listening/font/keyboard judgement: coordinator's CI watch and play.

Golden directories: `art`, `verdicts`, and the rich/plain pair for each of `critic-80`, `critic-120`, `preset-1-80`, `preset-1-120`, `preset-2-80`, `preset-2-120`, `preset-3-80`, `preset-3-120`, `staff-80`, `staff-120`, `title-80`, `title-120`.

### Negative drafts

Fixed code was committed before every plant. All local reds are genuine named assertions, not compile or format errors. No CI polling or labels by this lane; each immediate one-time listing returned `[]`, so run IDs and named CI outcomes are still for the coordinator to obtain.

| draft | head | expected Linux red | local result |
|---|---|---|---|
| #1 hidden fifth | `fe40f0e2085109c84dce72debce68a95dea0c677` | `test_hidden_fifth_is_never_accepted` | 63 pass / 2 fail, exit 1 |
| #2 generated repeat | `2daee263627f69b4c1cb64b715afb4a6cc9a3aae` | `test_census_ionian_50` and all five other modes | 58 pass / 7 fail, exit 1 |
| #3 green dissonance | `ae0af6149de89acca475917592bee77bf9ac27f1` | `test_dissonance_is_never_drawn_green` | 64 pass / 1 fail, exit 1 |

### Play and follow-ons

Mac binary: `/Users/mfwolffe/lanes/fg00/fugue/target/fugue`, SHA256 `6def495503bc660caa91a8c827c02ae288f3f838e0dccbeced61036dd0ae2a24`. Run it without flags for the illuminated title and tutorials; use `--seed 7 --size 120x40` for a seeded cantus above, `--plain` for the other tier, or `--mute`. Build evidence: `/Users/mfwolffe/lanes/fg00/mac-play-build.log` and `.exit`.

Engine follow-ons to file, not filed here: nonblocking output-owner poll/cancellation for prepared WAVs; decode CSI-u Enter/arrows/Escape/Space consistently with legacy keys (already noted by trail). PAX integration, measured physical font widths and actual timbre listening remain separate evidence. No planning or memory correction was written.

Pruned during work: lane-owned regenerated Linux `target/goldens`, `target/gameplay`, `src/.lu-cache`, and the generated test bytecode cache; the Linux cache accidentally copied to the Mac was removed without running it. Only exact fg00 paths were touched. The play worktree stays until play is accepted. Final prune and audit results are appended below after the PR opens.

## Done-when

- [x] Book I playable on pinned lair; original rules/art/text/music, named judge and two-tier manuscript.
- [x] Final-head Linux gate, goldens, verified recording, ear and performance green; one memory-gated Mac play build retained.
- [x] Three negative drafts open with local named red evidence.
- [x] Complete note carried in this PR body for materialisation; README current.
- [ ] Coordinator obtains/observes all three plant CI reds, then removes those drafts unmerged.
- [ ] Coordinator labels this final head for tier full, watches both host legs, accepts play and materialises this note before merge.
- [x] Required final-head audit run once and immediate CI run read recorded below; no lane wait or label.


### Final-head hand-back

PR #4 is at **996754bf3bef9df979370377ef9d5224ab0298a0**. The immediate one-time CI listing returned `[]`; the required audit subsequently identified **40260442000**, in progress at this exact head. No run was waited on or polled again.

The required command ran once from the org directory, direct exit **1**. Last line: **`AUDIT FAIL (footprint: cross-cutting)`**. Its failures are the in-progress head run/no green tier yet, the intentionally absent coordinator-owned full-matrix label, and the intentionally retained Mac play worktree. Ancestry, attribution, footprint, PR head, five note sections, all eleven cited shas and orphan checks passed. Log `/Users/mfwolffe/lanes/fg00/audit.log`, status `/Users/mfwolffe/lanes/fg00/audit.exit`.

Final pruning: the three exact clean Mac plant worktrees `/Users/mfwolffe/lanes/fg00/plant-hidden`, `/Users/mfwolffe/lanes/fg00/plant-repeat`, `/Users/mfwolffe/lanes/fg00/plant-colour` were removed individually, without force. On kasumi only `/home/mfwolffe/lanes/fg00/fugue/target/native`, `target/release`, `target/goldens`, `target/gameplay`, `src/.lu-cache` and `tests/__pycache__` were removed. The final Linux `target/fugue`, toolchain, pty/audio captures, committed evidence and logs remain. No local/remote lane job remains running; the coordinator owns the CI watches. Keep the Mac play worktree until play is accepted.

