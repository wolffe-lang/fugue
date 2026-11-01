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
