# r41q — fugue to lair `df11d213` (wolf 0.2.36 / lupin 0.1.58)

_fugue's part of r41q (the apps, the games and the docs to the published pair), after the engine's (lair#26)._

## Prediction

Written before the first change (2026-11-01, base trunk at `lair.pin` `9a65bf54`).

- `lair.pin` moves `9a65bf54` to **`df11d213`** (lair trunk, read twice). The eleven engine commits between
  are r41q's: the toolchain pin, three comments, `ci/games.conf` and notes. **No engine source changes**, so
  the only thing that moves under fugue is the compiler, 0.2.35 to 0.2.36, and the std.
- The engine's own toolchain file at `df11d213` names wolf 0.2.36 / lupin 0.1.58 / std `78b9d3cb` (lair#26,
  r41q's engine half): `.lair/tools/fetch-toolchain` accepts the linux x86-64 archives by digest and
  `.lair/tools/lib-toolchain.sh` accepts `wolf 0.2.36 (wolfgang, pin 5adf3d9)`, `lupin 0.1.58 (wolf-interp,
  reference interpreter at pin a5378e3)` and `STD-REV` `78b9d3cb`. No source here declares the names 0.2.36
  adds to the prelude (`VaList`, the four `va_*`, `env_arg0`, `env_args_bytes`), so `--deny-warnings` sees
  no W0304.
- `tier pr` (`plan-test`, `linux`) stays green with every count as at trunk (its last nightly, run
  41194689726): **227 tests, zero SKIPs**, both builds, **354 golden lines ok, zero DIFFERS**, **47 pty rows
  ok**, the gameplay, staff, species, pitch and fugue checks, `--event-reachable` on both tiers.
- `tier full` adds the macOS leg and the perf gate; the orchestrator labels and watches it.

## Forbidden

No merge, label, tag, release, issue filed or closed; no attribution trailer. No build on the Mac; local
runs on hasu block B alone, both lock names held per run; kasumi not touched. No other implementation's
source read. No source, test, golden, tool or workflow of fugue changed: `lair.pin`, this note and nothing else.

## Inputs verified

- Base: fugue trunk `8b7a02d2`, as the contract read it on 2026-10-31; trunk's last nightly (41194689726)
  green at the old pin with 227 tests, 354 golden lines, 47 pty rows.
- The engine between `9a65bf54` and `df11d213`: eleven commits, none in `src/` (`git diff --stat -- src`
  empty), so the compiler and the std are all that move.
- What waits for this pin: nothing in fugue's notes, issues (none open) or README names 0.2.36 or the next
  pin. `src/fugue.lu`'s comment on 0.2.35's release-tier miscompile describes why the selftest exists and
  stays true (wolf-lang#940's fix is after 0.2.36; the engine keeps `WOLF_MIDEND=0`).
- README read: it names no compiler version and its counts are fugue's own rows; current.
- lair trunk read twice before the pin was written (`git ls-remote` at 00:55:19Z and 00:55:21Z, and the
  commits API): `df11d213785f7694bdf3f3572299abc550d8b903`, lair#26's merge (r41q's engine half). The
  digests behind it are lair#26's: the release API read twice, every pinned archive hashed twice, the
  identities read from the archives; this repo's gauntlet holds the staged `.lair/wolf-toolchain.toml` to
  the same two API passes by script (`engine-pin`).
- 0.2.36's prelude names (`VaList`, the four `va_*`, `env_arg0`, `env_args_bytes`): declared in no `.lu`
  file here, so no W0304 under `--deny-warnings`.

## Evidence index

- `468779a` Predict lair.pin at df11d213 moves no frame
- `3e21b42` lair.pin: the engine at df11d213 (wolf 0.2.36 / lupin 0.1.58)
- The gauntlet at the final head, on hasu block B (`/home/mfwolffe/lanes/r41q/bin/gauntlet-game.sh fugue
  <sha>`, its log under `/home/mfwolffe/lanes/r41q/logs/`): the head asserted, `lair.pin` against lair's
  trunk read live, `tools/fetch-lair` (the
  staged `LAIR-REV` asserted), the staged engine's toolchain file proved against the API passes, the
  planner's tests, the image `localhost/r41q-pack-ci:fbee7e864f7dbee6`, `.lair/tools/fetch-toolchain`, then
  `tools/check-linux` in the container on CPUs 6-11, and the count (every test ok, zero FAILED, zero SKIP,
  the game's and the engine's split by path). Every step prints `END <step> exit=N`; the wrapper stops at
  the first nonzero one. The END lines and the counts are in the PR body.

## Done-when

The PR is open at its final head with `tier pr` green there, `Footprint: cross-cutting` (a pin), the audit
run once and passing but for the labelled `tier full`, which the orchestrator labels and watches (the
second host's goldens). Nothing to close or file here.
