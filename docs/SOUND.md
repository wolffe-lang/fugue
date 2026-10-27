# Sound

The cantus uses the engine's soft organ at p, panned slightly left; the player's
voice uses choir at mp, slightly right. Both are synthesized, with no sampled
music or sound fonts. These are provisional listening choices, not a claim of
physical speaker or headphone evaluation by the automated tests.

At page setup, `sound.prepare` renders the page's complete sounding register
(C1–B6 in Books I–V), plus every permitted cadence accidental in that register.
Book VI pages can supply C3–C7 and both sharp/flat spellings. Each audition has a quarter-second
note and its release inside a one-second 48 kHz stereo S16_LE WAV. Arrow edits and
Space select a prepared file; they do not synthesize on a frame tick. h prepares
both voices in one part-format score and plays that WAV, one whole note per second.
Rendering time is excluded from playback's tick deadline. Tests retain and inspect
the actual note bank and two-voice WAV, rather than substituting a click.

macOS starts `/usr/bin/afplay` with an argv vector. Both child stdout and child
stderr always go to `/dev/null`, including when audio tracing is enabled. The
adapter opens it for writing with `fs.open_append`, hands that handle to
`process.set_stdout` and `process.set_stderr`, then closes the parent's copy
on every spawn/error path. These pinned wolf-std setters build the descriptor
map used by `os_spawn_fds`: `[1, handle, 2, handle]`. No shell, terminal-global
redirection, engine modification or output-reading thread is involved.

Only one audition may be alive. Before Up/Down, # or Space starts a cached note,
the adapter polls, kills the previous audition if still owned, and waits for its
raw exit status to reap it. If reaping fails, no replacement is started. The
handle slot is cleared both on ordinary exit and on replacement. h also stops
the audition before rendering its whole-page WAV; that whole-page player has
its own owner and is not mistaken for an audition. Nonblocking polling still
reaps normal exits, and the 32-owner capacity guard remains a last resort, not
a queueing policy. Ordinary teardown restores the terminal before waiting for
remaining children and deleting the exclusive temporary WAV directory.

Linux is deliberately a WAV sink: auditions rewrite one `audition.wav`, even
with an explicit retained directory; they do not accumulate one file per key.
Whole-play handoffs keep their separate numbered output (rotating in the
private default directory). The same rendered files are written without
requiring an audio server or a package install. `FUGUE_WAV_DIR=path` keeps them in
an explicit directory for inspection or playback elsewhere; otherwise the private
directory is removed at exit. `--mute` or `FUGUE_SOUND=0` disables preparation
and output while keeping the deterministic visual pass.

The engine's WAV owner has only a blocking finish operation, not a nonblocking
reap or cancellation API. Fugue therefore owns the small afplay adapter through
wolf-std rather than calling the engine's blocking finish from its frame loop.
It still uses the engine's reader, synthesis, prepare and WAV encoding unchanged.


`--sound-replay FILE` writes raw 48 kHz stereo S16_LE PCM for the written score
at the end of a replay (`--script FILE --frames N`), or the initial seeded page.
It does not start an audio player. The live `h` path uses the same renderer,
with exactly one second per bar rather than an extra second of silent padding.
The committed `tests/goldens/audio/whole-seed7.sha256` pins all 1,920,000 PCM
bytes of the ten-bar seed-7 piece. Both compiled backends export and compare it;
the pty row independently compares the actual `h` WAV's payload to that digest.
Every bar has nonzero energy in both channels, no clipped samples, and a stereo
RMS ratio below 2. Distinct timbres and p/mp dynamics (five dB favouring the
choir), with opposing modest pans, are retained; listening remains the final
judgement of their balance, not a claim inferred solely from stereo RMS.

`FUGUE_AUDIO_TRACE=1` logs whole-render, output-start and player-end evidence.
Redirect stderr to a file when using this diagnostic in a real terminal;
otherwise diagnostics could move the terminal cursor outside the draw pen.
Normal play does not emit per-cue diagnostic lines. The Mac pty row requires
an owned `/usr/bin/afplay` child with the whole WAV argument, observes it alive,
and waits for its successful exit and reap. These opt-in lines are fugue's own
stderr, not afplay's: redirect them explicitly while tracing. Linux's named WAV sink is not
claimed as speaker evidence. A rendered file without the output handoff fails.

## Rhythmic books

Books II–V send their written values and outgoing ties to the same part reader.
A whole still lasts one second; a half, quarter and eighth divide that time
exactly. Incoming editor ties become outgoing `~` marks in the score text.
The viewport and note lights follow this same clock. The later-book note bank
also contains the permitted cadence accidentals in the editable register.

The rhythmic audio gate compares the complete PCM with each isolated voice,
checks its exact duration and nonzero samples on both compiled backends, and
a live Book V terminal row verifies that h reaches the existing output owner.
These checks do not claim a physical loudspeaker or headphone listening test.


`--pitch-proof DIR` exports the initial cantus/editor notes on every preset and
three seeds per book, plus every preset reference answer, and one PCM file per
distinct spelling. `tools/pitch-check.py` independently checks the names and
fixed-clef row coordinates and estimates each PCM fundamental by FFT. The peak
search is not centred on the expected frequency; it groups window/vibrato
sidebands and finds the lowest significant spectral peak. Every measured
fundamental must lie within one percent of equal temperament.

The note-bank timing diagnostic is also opt-in through `FUGUE_AUDIO_TRACE=1`.
Normal page changes do not print preparation text into the terminal drawing.
Left/Right navigation never prepares or auditions sound. Up/Down starts the
already prepared WAV; a pty witness checks that twenty such auditions leave
every note-bank file unchanged and emit no further preparation event.

## The fugue's entries

Book VI uses three named tracks but only two musical voices at once. The
subject's organ sounds alone for six bars; its organ continuation then plays
the countersubject while the choir enters with the answer. Explicit rests keep
the entries aligned. The twelve-bar exposition lasts exactly twelve seconds
on the shared clock. `h`, replay PCM export and the entry lights all use that
same written pair. No third entry or closing cadence is synthesized off-screen.
The Book VI audition bank includes natural, sharp and flat spellings throughout
its editable C3–C7 range; preparations still happen outside frame rendering.

## Player ownership witnesses

The sound-owner rows in `tests/ear_rows.py` join stderr to the actual pty. On
macOS, `quiet-player-stderr` replaces the prepared notes with empty WAVs and
requires that a failing real afplay leave every terminal text/style cell
unchanged. `audition-storm` sends forty # keys in two seconds, polls the game's
own children, checks at most one audition, and compares every captured frame
with the two states from an independent muted run. The accidental's pitch,
interval and judge labels may legitimately change too; no rectangular region
is ignored. Every press must produce its expected frame with p99 <=70 ms.
`audition-hear-owner` verifies h kills/reaps the audition before handing its
whole WAV to a distinct live afplay. Linux's `linux-audition-sink` row sends the
same storm and requires exactly one rewritten audition file, with all forty
keys recorded. These rows run through the existing game pty gate, without a
new workflow or an audio-server dependency.
