# Sound

The cantus uses the engine's soft organ at p, panned slightly left; the player's
voice uses choir at mp, slightly right. Both are synthesized, with no sampled
music or sound fonts. These are provisional listening choices, not a claim of
physical speaker or headphone evaluation by the automated tests.

At page setup, `sound.prepare` renders fifteen diatonic pitches over two octaves,
plus the raised cadence seventh where needed. Each audition has a quarter-second
note and its release inside a one-second 48 kHz stereo S16_LE WAV. Arrow edits and
Space select a prepared file; they do not synthesize on a frame tick. h prepares
both voices in one part-format score and plays that WAV, one whole note per second.
Rendering time is excluded from playback's tick deadline. Tests retain and inspect
the actual note bank and two-voice WAV, rather than substituting a click.

macOS starts `/usr/bin/afplay` with an argv vector. The game polls only children
it owns through wolf-std and reaps them nonblocking. There are at most 32 live
cue owners; failure is named silence. Ordinary teardown restores the terminal
before waiting for remaining children and deleting the exclusive temporary WAV
directory. The default sink rotates audition and whole-play files to stay bounded.

Linux is deliberately a WAV sink: the same rendered files are written, without
requiring an audio server or a package install. `FUGUE_WAV_DIR=path` keeps them in
an explicit directory for inspection or playback elsewhere; otherwise the private
directory is removed at exit. `--mute` or `FUGUE_SOUND=0` disables preparation
and output while keeping the deterministic visual pass.

The engine's WAV owner has only a blocking finish operation, not a nonblocking
reap or cancellation API. Fugue therefore owns the small afplay adapter through
wolf-std rather than calling the engine's blocking finish from its frame loop.
It still uses the engine's reader, synthesis, prepare and WAV encoding unchanged.
