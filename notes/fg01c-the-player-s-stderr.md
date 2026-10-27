# fg01c — the player's stderr, and one audition at a time

_Materialised from fugue#27's body at the merge (`aa76ae1e`); the Codex wrapper writes no .md notes._


# fg01c — the player's stderr and the audition storm

The wrapper prohibits Markdown report files. This PR body is the full five-section note for the coordinator to materialise as notes/fg01c-the-player-s-stderr.md on trunk.

## Prediction

Committed before implementation in the original prediction commit, now rebased as `e6b3481` (notes/fg01c-prediction.txt): expect 8–20 afplay children during forty 20 Hz auditions, up to the 32-owner guard; expect inherited player stderr to damage staff cells, with an invalid WAV making the error deterministic. Expected p99 below 70 ms unless concurrent startup contended.

The population prediction was low: unchanged trunk's forty-press storm reached 32 owned children. The real afplay invalid-WAV row changed 1,108 text cells and 40 style rows. The original storm capture had up to 78 unexpected text cells; the final timing witness still rejects trunk with 32 children, 53 unexpected text cells and only 32 valid expected frames out of forty keys. Full correct-frame p99 is undefined on that failing run, not green. The first harness's 48.844 ms p99 covered only its 29 observed responses and is not a forty-key success claim.

R-fg01c-1: recommend A, implemented. An audition means the note being edited; keeping two simultaneously obscures which pitch is under inspection. Kill and reap the prior audition before starting its replacement. h stops the audition before whole-page rendering, and whole playback retains a separate owner. The 32-owner guard remains the final guard.

## Forbidden

No engine, pin, runtime, compiler, session/editor semantics, CI workflow, package installation, label, merge, tag, issue action, planning-repo or memory change. Changed implementation is only src/ear/ear.lu, with sound docs and tests, the contract's evidence/prediction, and the owed README-only count refresh. No attribution trailers.

Mac worktrees and all scratch, HOME and TMPDIR are under /Users/mfwolffe/lanes/fg01c/. Every Mac build or test runs through a scripted vm_stat gate requiring at least 8 GiB free+inactive; no gate was lowered. Native proof and plant builds are test binaries. The final release play build is made once at the final rebased head.

Linux gates run in hasu's existing localhost/pack-ci:fbee7e864f7dbee6 rootless image, with --memory 12g, under /home/mfwolffe/lanes/hasu-block-B.lock and taskset -c 6-11 inside. No process outside the test's owned children is signalled.

## Inputs verified

Read the contract, screenshot and RULES sections 1–10, current adapter, SOUND.md, fg01b note and its pty/latency tooling, and spec/11-os.md [os.proc.fds] and [os.proc.spawn]. The pinned standard library already serves process.set_stdout and process.set_stderr. They build the os_spawn_fds descriptor map [1, quiet.fd, 2, quiet.fd] onto a writable /dev/null opened with fs.open_append. The parent closes its handle with defer on success or error. Both child streams stay null-routed even when FUGUE_AUDIO_TRACE is enabled; the existing opt-in game trace remains the caller's stderr diagnostic and is documented separately. No shell or lair change is needed.

A dedicated audition slot distinguishes it from whole playback. Normal polling clears both its list entry and slot; replacement polls, kills that exact owned child and waits for its raw status before clearing/reusing the slot. A reap failure prevents starting a replacement. Linux auditions now rewrite one audition.wav, including explicit FUGUE_WAV_DIR retention; whole-play handoffs retain their existing separate numbered path.

The full pinned toolchain pair is reused from fg01b's verified archives, not a source build: wolf 0.2.35, lupin 0.1.56, bundled std 2386522e, unchanged lair 57870143. Release asset digests were fetched twice and matched the pin; installed Mac driver, worker, interpreter and runtime hashes were read twice. Durable records are /Users/mfwolffe/lanes/fg01c/{wolf,lupin}-release-{1,2}.json and mac-tools-{1,2}.sha256.

Rebased onto fg02's merged trunk c7bcc84. Two append-only conflicts retained both lanes' additions in tests/pty_rows.py and docs/SOUND.md. README read against the rebased change and refreshed in a README-only commit: 178 checked tests unchanged; full terminal gate now 38 rows on Linux / 40 on macOS.

## Evidence index

Implementation and tests:
- `e6b3481` — prediction before implementation.
- `511a877` — two named live Mac regressions first, sharing the existing pty gate.
- `5c88d00` — null-routed players and single-audition replacement.
- `4ee9359` — h ownership witness, host-specific Linux sink row, formatting.
- `9e2a802` — redirect, ownership and test documentation.
- `62ed5da` — retained trunk and plant evidence.
- `848d2a2` — independent frame timestamps rather than fifty-ms send-slot sampling.
- `aa76ae1` — README-only count refresh, final head.

### Witness accounting correction

The original native storm appeared to have 38/40 separate frames. Investigation showed two witness mistakes: it treated the fifty-ms send interval as the response deadline despite a seventy-ms contract, and then merged distinct close-together terminal writes while trying to fix that. The final row sends forty keys within two seconds independently of reads, timestamps completed terminal states, compares every glyph/style against the exact two states from a separate muted run, preserves distinct nearby states and allows only a bounded split-write completion. It publishes a per-press p99 only when all forty expected transitions are observed. Actual key recordings must contain all forty sharp keys. The independent reference has 25 intentionally changed text cells (accidental and its pitch/interval/judge labels), not a masked staff rectangle.

The corrected native Mac storm is green: forty expected frames, max one child, p99 48.299 ms, zero extra cells. The muted diagnostic also had forty frames. Thus no lair input-coalescing or fugue latency issue is established by the earlier false reds; do not file an engine issue on those numbers. Both genuine trunk faults remain named reds under the final witness, recorded in /Users/mfwolffe/lanes/fg01c/mac-before-final-witness.log and notes/fg01c-evidence/mac-before-final-witness.txt.

Durable pre-fix captures: /Users/mfwolffe/lanes/fg01c/mac-before-evidence/. Corrected trunk log: /Users/mfwolffe/lanes/fg01c/mac-before-final-witness.log. Corrected native fixed log: /Users/mfwolffe/lanes/fg01c/mac-native-storm-final-witness.log; retained capture/journal /Users/mfwolffe/lanes/fg01c/mac-native-after/audition-storm/. Checked-in evidence is under notes/fg01c-evidence/.

### Plants

- Draft #25, `5cf2a14`, fg01c-plant-stderr: remove only process.set_stderr. Mac native build succeeds; quiet-player-stderr exits 1 by name with 1,108 changed text cells / 40 style rows and an afplay diagnostic in the pty. Memory gate 10.46 GiB. /Users/mfwolffe/lanes/fg01c/plant-stderr.log and plant-stderr.exit (1).
- Draft #26, `98dbc71`, fg01c-plant-overlap: remove only stop_audition from audition, retaining both stream maps and h's stop. Mac native build succeeds; audition-storm exits 1 by name: 32 children alive, wanted <=1; forty keys recorded. Memory gate 10.59 GiB. /Users/mfwolffe/lanes/fg01c/plant-overlap.log and plant-overlap.exit (1).

Both fixes preceded both plants. These are module-local planted reds, recorded in /Users/mfwolffe/lanes/fg01c/plant-stderr.log and /Users/mfwolffe/lanes/fg01c/plant-overlap.log; no CI dispatch or CI wait was performed. The coordinator owns retiring the two unmerged drafts.

### Final-head gates and play

Final head: aa76ae1e3a2a4ef3d01e1286626f6f1c16697b27, based on merged fg02 trunk c7bcc84. No subsequent source change or build is pending.

Linux full gate at that exact head: exit 0. tools/check-linux (fmt; 178 checked tests, 0 failed/rejected/unsupported and 0 SKIP lines; both builds; selftest; both-backend goldens; all 38 terminal rows; gameplay, pitch/PCM and Book VI censuses), followed by native linux-audition-sink and tools/check-perf. Release and native sink storms each recorded forty keys, forty expected frames, zero extra cells and one audition file, verified byte-for-byte against the final natural C3 bank WAV. Recorded frame p99s were 34.266 / 24.053 ms respectively; the Linux contract gates bounded file count, not a native audio timing claim. Gate marker/log/status: /home/mfwolffe/lanes/fg01c/linux-gate.{head,log,exit} (0). The pre-rebase green is retained separately and is not substituted for this exact-head run. No Linux job remains running.

The single final Mac release play build passed its 11.21 GiB free+inactive gate, exit 0; final interaction passed its independent 11.09 GiB gate, exit 0. Tested the copied play artifact itself, not a differently named rebuild. All eight selected real-pty rows are green: quiet-player-stderr, audition-storm, audition-hear-owner, cached-arrow-auditions, quiet-audio-page-change, hear-whole-is-played, fugue-exposition-record and fugue-junk-120-rich. The last two retain fg02's twelve-second real exposition handoff and all-cell repaint proof.

Final Mac invalid-WAV row: zero changed text cells, zero style rows, no failed player left alive. Final storm: forty presses over 1,953.297 ms, forty expected frames and recorded keys, at most one real afplay child at every poll, p99 39.840 ms (bar 70), zero extra cells and no AudioQueueStart/error text. The twenty-five intentional accidental/status cells match the independent muted reference. h retired its owned audition in 25.606 ms and started a separate whole-page child. The existing whole-play row observed successful exit and reap; exact ten-bar PCM remained pinned.

Durable Mac final log/status: /Users/mfwolffe/lanes/fg01c/mac-final-pty.{log,exit} (0). Build marker/log/status: /Users/mfwolffe/lanes/fg01c/mac-play-build.{head,log,exit} (0). Final forty-key per-press timestamps, every process poll, raw completed-frame captures and recording: /Users/mfwolffe/lanes/fg01c/mac-final-evidence/audition-storm/. Invalid-WAV and h ownership journals are adjacent under mac-final-evidence/; all are preserved outside the checkout.

Play command (sound enabled, Book V at 120x40):

```
/Users/mfwolffe/lanes/fg01c/fugue-play-aa76ae1e --book 5 --size 120x40 --no-title
```

Binary SHA256: ad6e2d74514cfa1b9ea180116683fe4b6dd3cac15177857b9f4c72919da2c887. Both the terminal rows and the run command use this artifact. No physical speaker judgement is claimed.

PR #27. The immediate one-time CI listing at this final head returned [] (no run visible yet), recorded in /Users/mfwolffe/lanes/fg01c/ci-once.json. It was not polled or waited on. The required single audit independently found CI run [40436973926](https://github.com/wolffe-lang/fugue/actions/runs/40436973926) in progress at that head. The coordinator owns watching it and merges only after its PR tier is green.

The audit ran exactly once from /Users/mfwolffe/GithubOrgs/wolffe-lang:

```
bash wolf/tools/lane-audit.sh fugue fg01c 27 /Users/mfwolffe/lanes/fg01c/fugue
```

Direct exit 1. Exact last line: `AUDIT FAIL (footprint: module)`. Log/status: /Users/mfwolffe/lanes/fg01c/audit.{log,exit}. It passed ancestry, no-attribution, module path scope, PR head, all five sections, every cited commit and no-orphan checks. Four FAIL lines were reported: two for in-progress CI/no completed green tier; one missing inline artifact citation in a paragraph restating the earlier reds; one for the Mac worktree still being present. The citation has since been added to that exact paragraph. After preserving the complete Mac target evidence and toolchain, all three exact clean Mac lane worktrees were retired without force; no shared or other lane worktree was touched. Those two non-CI findings are corrected after the recorded audit, not claimed as a rerun or as AUDIT CLEAN. The once-only audit was not repeated.

Full Mac target evidence now lives at /Users/mfwolffe/lanes/fg01c/mac-final-target/ (including pty/, native/release binaries and waveform evidence). The complete verified toolchain is /Users/mfwolffe/lanes/fg01c/mac-toolchain/. Plant raw pty evidence is /Users/mfwolffe/lanes/fg01c/plant-stderr-evidence/ and plant-overlap-evidence/. The final play binary, all logs, per-press final-evidence directory and Linux clone remain available. No lane-started job remains running.

## Done-when

- [x] Child stdout/stderr redirected; invalid real player cannot damage the terminal.
- [x] R-fg01c-1 A implemented; replacement kills/reaps only the owned audition; h retains its own player.
- [x] Forty-key storm, exact cells/styles, process polls and seventy-ms p99 gate; bounded Linux sink.
- [x] Both named trunk reds, both draft plants red locally, sound docs and README refreshed.
- [x] Final-head Linux and Mac evidence and the single release play binary.
- [x] Immediate CI read and single audit recorded above, with exact FAIL output and subsequent corrections disclosed.
- [ ] Coordinator watches CI, accepts physical play, retires plant drafts and materialises this note.

No issue was filed or closed. No physical loudspeaker/headphone judgement is claimed by automated pty and WAV evidence.

