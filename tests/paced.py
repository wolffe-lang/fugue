"""tests/paced.py: the trace-keyed injector every fugue pty row types through (fg04, fugue#36).

The game's live loop (src/fugue.lu) reads the terminal when it wakes, applies
every key it read on that wake's first due tick, steps every due tick and draws
once. With --trace it then prints, on its own stderr,

    trace output frame F bytes N            frame F's write boundary: N bytes since the first frame
    trace frame F carries_key inner_us U    when frame F applied a key

A busy host makes a wake late: several ticks fall due at once and every key read
on that wake is applied on the first (lair's clock, docs/KEYS.md), so a key the
row wrote for one tick can be applied ticks later, beside the next one. So the
rows never decide anything by a sleep:

  * a byte is written only once the game has drawn (its first frame, then the
    acknowledgement of the previous write) and, when a row schedules it at a
    tick, once the trace shows the tick before its target;
  * a write is acknowledged by the game's own trace: a single carrying key by
    its carrying frame (the first `carries_key` line after the write; nothing
    else is outstanding), any other write by the second output frame traced
    after the write, since that frame's wake read after the write. The game
    reads at most 256 bytes a wake, so writes are cut at key boundaries;
  * a frame is judged cut at its exact output boundary, never at whatever bytes
    the row happened to hold when it read a trace line;
  * after the session, every key the game recorded belongs to the first
    carrying frame after its record tick, and that frame must be one its write
    was acknowledged by (`verify`): an injector that misreads a tick is red;
  * a late byte is input, never a verdict. A session a stall pushes out of its
    case is driven again (`redrive`), up to REDRIVES sessions, every re-drive
    printed; a case never realised is a SCHEDULE failure; no re-drive forgives a
    disagreement.

Loaded by path (`runpy.run_path`), never imported: the runner runs under `-I`.
"""
import os
import re
import select
import time

OUT_LINE = re.compile(rb'trace output frame (\d+) bytes (\d+)\n')
KEY_LINE = re.compile(rb'trace frame (\d+) carries_key inner_us (\d+)\n')
# A game that answers nothing for a minute is hung: that bound is liveness, not
# a timing verdict, and is never what decides a row.
LIVENESS_S = 60.0
REDRIVES = 4
# term.read_keys(256): the most one wake reads.
READ_MAX = 256
QUERY = b'\x1b[?u'
PUSH = b'\x1b[>11u'
POP = b'\x1b[<u'
LEAVE = b'\x1b[0m\x1b[?25h\x1b[?1049l'
TICK_S = 1 / 30


class Unrealised(Exception):
    """A stall pushed the session out of its case: never a verdict on the game."""


def keys_of(data):
    """Typed bytes cut at key boundaries: ESC [ params final, ESC O x, else one byte."""
    keys, i = [], 0
    while i < len(data):
        if data[i] == 0x1b and i + 1 < len(data) and data[i + 1] == 0x5b:
            j = i + 2
            while j < len(data) and not 0x40 <= data[j] <= 0x7e:
                j += 1
            keys.append(data[i:j + 1]); i = j + 1
        elif data[i] == 0x1b and i + 2 < len(data) and data[i + 1] == 0x4f:
            keys.append(data[i:i + 3]); i += 3
        else:
            keys.append(data[i:i + 1]); i += 1
    return keys


def pieces(data, limit=READ_MAX):
    """Whole keys, at most `limit` bytes a write."""
    out, cur = [], b''
    for k in keys_of(data):
        if cur and len(cur) + len(k) > limit:
            out.append(cur); cur = b''
        cur += k
    if cur:
        out.append(cur)
    return out


def recorded(path):
    """The game's own recording: [(tick, key name)] in order."""
    keys = []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    for line in text.splitlines():
        w = line.split()
        if len(w) >= 3 and w[0] == 't':
            keys.append((int(w[1]), w[2]))
    return keys


# Every session a row starts through this module, until it finishes. A row
# that raises mid-session would otherwise leave its game alive: the pty's
# holder keeps the master open and never reads it, so the game blocks writing
# a full terminal and never sees its quit (trunk's enhanced row left one so).
LIVE = []


def tracked(ctx, base=None):
    """ctx.Session (or `base`), registered in LIVE until it finishes."""
    Base = base or ctx.Session

    class Tracked(Base):
        def __init__(self, *args, **kw):
            LIVE.append(self)
            super().__init__(*args, **kw)

        def finish(self, *args, **kw):
            try:
                return super().finish(*args, **kw)
            finally:
                if self in LIVE:
                    LIVE.remove(self)
    return Tracked


def end_live():
    """Quit and reap every session a failed row left running."""
    for s in list(LIVE):
        try:
            if not s.eof:
                os.write(s.master, b'q')
            s.finish(timeout=20)
        except Exception as e:
            print('paced: a session left by a failed row did not end: %s' % e, flush=True)
        if s in LIVE:
            LIVE.remove(s)


def guarded(row):
    """A row that ends every session it left running when it raises."""
    def run(bin, ctx):
        try:
            return row(bin, ctx)
        except BaseException:
            end_live()
            raise
    return run


def session(ctx, base=None):
    """A Session class on `base` (default ctx.Session) that reads promptly,
    parses the trace once a line, and types only through `send`."""
    Base = tracked(ctx, base)

    class Paced(Base):
        def __init__(self, argv, rows, cols, env, settle=0.0, replies=()):
            if '--trace' not in argv:
                raise AssertionError('a paced session needs --trace in its argv')
            self.outputs = []     # (tick, bytes since the first frame, err offset, time read)
            self.carrying = []    # (tick, inner_us, err offset, time read)
            self.acks = []
            self.writes = []
            self.out_marks = []   # (time read, len(out) after the read)
            self._parsed = 0
            self._entry = None
            self.argv = list(argv)
            super().__init__(argv, rows, cols, env, settle, replies)

        # -- reading ----------------------------------------------------
        def _ready(self, timeout):
            """The readable fds, waiting at most `timeout` s in poll(2): macOS
            coalesces select(2) timeouts in a background QoS clamp, not poll's."""
            waiter = select.poll()
            waiter.register(self.r_err, select.POLLIN | select.POLLHUP)
            if not self.eof:
                waiter.register(self.master, select.POLLIN | select.POLLHUP)
            return [fd for fd, _ in waiter.poll(timeout * 1000)]

        def pump(self, seconds):
            end = time.monotonic() + seconds
            while True:
                left = end - time.monotonic()
                self._take(self._ready(min(.002, max(0.0, left))))
                if left <= 0:
                    return

        def _take(self, ready):
            if self.master in ready:
                try:
                    chunk = os.read(self.master, 65536)
                except OSError:
                    chunk = b''
                if not chunk:
                    self.eof = True
                else:
                    self.out += chunk
                    self.out_marks.append((time.monotonic(), len(self.out)))
                    while self.replies and self.replies[0][0] in self.out:
                        query, answer = self.replies.pop(0)
                        observed = time.monotonic()
                        if os.write(self.master, answer) != len(answer):
                            raise RuntimeError('short stand-in terminal reply')
                        self.reply_times.append((query, observed, time.monotonic()))
            if self.r_err in ready:
                chunk = os.read(self.r_err, 65536)
                if chunk:
                    self.err += chunk
                    self._parse()

        def _parse(self):
            now = time.monotonic()
            pos = self._parsed
            while True:
                nl = self.err.find(b'\n', pos)
                if nl < 0:
                    break
                line = self.err[pos:nl + 1]
                m = OUT_LINE.match(line)
                if m:
                    self.outputs.append((int(m[1]), int(m[2]), pos, now))
                else:
                    m = KEY_LINE.match(line)
                    if m:
                        self.carrying.append((int(m[1]), int(m[2]), pos, now))
                pos = nl + 1
            self._parsed = pos

        def drain(self):
            """Read everything already written, without waiting."""
            while True:
                ready = self._ready(0)
                if not ready:
                    return
                before = (len(self.out), len(self.err), self.eof)
                self._take(ready)
                if (len(self.out), len(self.err), self.eof) == before:
                    return

        def wait(self, cond, what, bound=LIVENESS_S):
            deadline = time.monotonic() + bound
            while not cond():
                if self.eof:
                    self.drain()
                    if cond():
                        return
                    raise AssertionError('TRACE: the game ended before its %s' % what)
                if time.monotonic() >= deadline:
                    raise AssertionError('TRACE: no %s within %.0f s (the game is hung)' % (what, bound))
                self.pump(.002)

        # -- the trace --------------------------------------------------
        @property
        def tick(self):
            """The last frame the trace has shown, or -1 before the first."""
            return self.outputs[-1][0] if self.outputs else -1

        def entry(self):
            """Where the first frame starts in the terminal bytes: after the
            enter bytes, the keyboard query and (when negotiated) the push."""
            if self._entry is None:
                self.wait(lambda: QUERY in self.out, 'keyboard query')
                q = self.out.index(QUERY) + len(QUERY)
                self.wait(lambda: len(self.out) >= q + len(PUSH) or self.eof, 'first frame bytes')
                self._entry = q + (len(PUSH) if self.out[q:q + len(PUSH)] == PUSH else 0)
            return self._entry

        def negotiated(self):
            self.ready()
            return self.out[self.out.index(QUERY) + len(QUERY):].startswith(PUSH)

        def boundary(self, tick):
            n = next((n for t, n, _, _ in reversed(self.outputs) if t == tick), None)
            if n is None:
                raise AssertionError('TRACE: frame %d was never traced' % tick)
            return self.entry() + n

        def frame(self, tick=None):
            """The terminal bytes through frame `tick`'s output boundary
            (default: the last frame traced), once they have all arrived."""
            if tick is None:
                tick = self.tick
            b = self.boundary(tick)
            self.wait(lambda: len(self.out) >= b, 'bytes of frame %d' % tick)
            return self.out[:b]

        def ready(self):
            """The game's first frame, traced and arrived; its tick."""
            self.wait(lambda: self.outputs, 'first frame')
            self.frame(self.outputs[0][0])
            return self.outputs[0][0]

        def until(self, tick):
            """Wait for the trace to show frame `tick` or later."""
            self.wait(lambda: self.tick >= tick, 'frame %d' % tick)
            return self.tick

        def _line_after(self, tick):
            """Every line of frame `tick`'s iteration is parsed once a later
            frame is traced or its own carrying line has been read."""
            return any(t > tick for t, _, _, _ in self.outputs) or any(t == tick for t, _, _, _ in self.carrying)

        # -- writing ----------------------------------------------------
        def send(self, data, at=None, carries=True):
            """Write `data` paced and acknowledged; the last write's ack.

            `at`: the tick the first write is for (written once the trace
            shows `at - 1`). `carries`: a single key that the game applies
            (False for a release or a byte the game reads as nothing)."""
            ack = None
            for piece in pieces(data):
                ack = self._send_piece(piece, at, carries and len(keys_of(piece)) == 1)
                at = None
            return ack

        def _send_piece(self, piece, at, single):
            return self._ack(piece, self._write(piece, at), single)

        def _write(self, piece, at):
            """Write once the game has drawn and the trace shows `at - 1`;
            what the acknowledgement needs to know about the write."""
            if not self.outputs:
                self.ready()
            if at is not None:
                self.until(at - 1)
            self.drain()
            due_seen = None
            if at is not None:
                due_seen = next((when for t, _, _, when in self.outputs if t >= at - 1), None)
            w = {'piece': piece, 'target': at, 'err_at': len(self.err),  # every line before: before the write
                 'traced': self.tick, 'due_seen': due_seen, 'written': time.monotonic()}
            os.write(self.master, piece)
            self.drain()
            w['drained'] = len(self.err)  # every line after: after the write
            self.writes.append(w)
            return w

        def _ack(self, piece, w, single):
            err_at, drained = w['err_at'], w['drained']

            def mine():
                return [c for c in self.carrying if c[2] >= err_at]

            def after():
                return [o for o in self.outputs if o[2] >= drained]

            if single:
                self.wait(lambda: mine() or len(after()) >= 2, 'carrying frame for %r' % piece)
                if not mine():
                    self.wait(lambda: self._line_after(after()[1][0]), 'end of frame %d' % after()[1][0])
                if not mine():
                    raise AssertionError('ACK: %r was read and applied in no carrying frame' % piece)
                frame = mine()[0][0]
            else:
                self.wait(lambda: len(after()) >= 2, 'second frame after %r' % piece)
                frame = after()[1][0]
                self.wait(lambda: self._line_after(frame), 'end of frame %d' % frame)
            carried = [c[0] for c in mine() if c[0] <= frame]
            self.frame(frame)
            ack = {'bytes': piece.hex(), 'keys': len(keys_of(piece)), 'single': single, 'target': w['target'],
                   'traced_at_write': w['traced'], 'written': w['written'], 'frame': frame, 'carried': carried,
                   'boundary': self.boundary(frame), 'acked': time.monotonic(),
                   'inner_us': next((u for t, u, _, _ in self.carrying if t == frame), None)}
            self.acks.append(ack)
            return ack

        def write_at(self, key, at):
            """Write one key once the trace shows `at - 1`, without waiting for
            its acknowledgement (a stream the game may read several of on one
            late wake); `settle` acknowledges the stream."""
            return self._write(key, at)

        def settle(self, first):
            """Acknowledge every write since `first` (a write_at record) at once:
            the second output frame after the last write, every carrying frame
            since the first."""
            last = self.writes[-1]
            i = next(i for i, w in enumerate(self.writes) if w is first)
            ack = self._ack(b''.join(w['piece'] for w in self.writes[i:]),
                            dict(last, err_at=first['err_at']), False)
            ack['target'] = first['target']
            return ack

        def burst(self, key, count, every=1):
            """`count` presses of `key`, one each `every` ticks by the trace,
            each acknowledged by its carrying frame; the acks."""
            start = self.tick + 1
            return [self.send(key, at=start + i * every) for i in range(count)]

        # -- after the session -------------------------------------------
        def verify(self, record, name, problems):
            """Every recorded key against the frame its write was acknowledged
            by; the terminal's tail after the last frame. The recorded keys."""
            keys = recorded(record)
            frames = [c[0] for c in self.carrying]
            mapped = []
            for t, k in keys:
                f = next((c for c in frames if c > t), None)
                if f is None and k != 'quit':
                    problems.append('%s: ACK: recorded %s at tick %d has no carrying frame' % (name, k, t))
                mapped.append(f)
            acked = []
            for a in self.acks:
                acked.extend(a['carried'])
            wanted = sorted({f for f, (_, k) in zip(mapped, keys) if f is not None and k != 'quit'})
            if sorted(set(acked)) != wanted:
                problems.append('%s: ACK: acknowledged frames %s, the recording carries %s' % (
                    name, sorted(set(acked))[:12], wanted[:12]))
            singles = [a for a in self.acks if a['single']]
            for a in singles:
                n = sum(1 for f in mapped if f == a['frame'])
                if a['carried'] != [a['frame']] or n != 1:
                    problems.append('%s: ACK: a single key acknowledged by frame %d, which carries %d recorded keys' % (
                        name, a['frame'], n))
            if self.outputs and self.eof is not None:
                tail = self.out[self.entry() + self.outputs[-1][1]:]
                if tail not in (LEAVE, POP + LEAVE):
                    problems.append('%s: TRACE: bytes after the last frame are not the leave bytes: %r' % (name, tail[:40]))
            return keys

        def arrived(self, boundary):
            """When the row first held `boundary` bytes of output."""
            return next((t for t, n in self.out_marks if n >= boundary), None)

        def lateness(self):
            """Ticks each scheduled write was applied after its target."""
            return [a['carried'][0] - a['target'] for a in self.acks if a['target'] is not None and a['carried']]

    return Paced


# A quiet Mac's poll(2) wakes within 3 ms of its deadline, at default QoS and in
# the background clamp alike; a wake later than this is the host's doing.
STALL_SLACK_S = 0.005
# A latency sample the host stalled is not the game's: a session that could
# not measure is driven once more (a transient load passes), then the bar is a
# loud, counted SKIP naming what the probe saw. Every frame is still judged.
LATENCY_SESSIONS = 2

PROBE = r'''
import os, select, sys, time
TICK = 1 / 30
start = time.monotonic(); k = 1
waiter = select.poll(); waiter.register(0, select.POLLIN | select.POLLHUP)
sys.stderr.write('start %%.6f\n' %% start); sys.stderr.flush()
while True:
    due = start + k * TICK
    ready = waiter.poll(max(0.0, due - time.monotonic()) * 1000)
    now = time.monotonic()
    if ready and not os.read(0, 1):
        break
    if ready:
        continue
    if now - due > %(slack)f:
        sys.stdout.write('%%.6f %%.6f\n' %% (due, now - due)); sys.stdout.flush()
    k = int((now - start) / TICK) + 1
'''


class StallProbe:
    """The host's stalls, measured by a process of their own that waits the
    way the game does: a 30 Hz timed poll(2) (lair's clock waits in poll;
    macOS coalesces select(2) and sleep timeouts in the background QoS
    clamp by up to 200 ms but not poll's), catching up when it wakes late.
    A tick it wakes for more than `slack` late is a stall (the tick's due time
    and the lateness, on the monotonic clock every process shares). It runs in
    the row's scheduling class, ends when its stdin closes (no signal), and
    sees the host's timers and CPU, never the game's own work: a blocking
    handoff in the game does not make it late.

    It vouches only for the time it ran. The constructor returns once the
    probe's own script is running (its first line, `start T`, read from its
    stderr), so neither its start-up (15-24 ms of a core in the clamp,
    `notes/fg04-evidence/probe-gap.py`) nor an unmeasured stretch falls in the
    window a row opens next; and a window opening before `started` reads as
    stalled for the stretch the probe did not see, never as on time."""

    def __init__(self, scratch, slack=STALL_SLACK_S):
        import subprocess, sys
        self.path = os.path.join(str(scratch), 'stall-probe.txt')
        self.out = open(self.path, 'w')
        self.proc = subprocess.Popen([sys.executable, '-I', '-c', PROBE % {'slack': slack}],
                                     stdin=subprocess.PIPE, stdout=self.out, stderr=subprocess.PIPE)
        self.stalls = None
        waiter = select.poll(); waiter.register(self.proc.stderr, select.POLLIN | select.POLLHUP)
        line = self.proc.stderr.readline() if waiter.poll(LIVENESS_S * 1000) else b''
        if not line.startswith(b'start '):
            self.proc.stdin.close(); self.proc.wait(); self.out.close()
            raise RuntimeError(f'the stall probe did not start within {LIVENESS_S:.0f} s: {line!r}')
        self.started = float(line.split()[1])

    def stop(self):
        self.proc.stdin.close()
        self.proc.wait()
        self.proc.stderr.close()
        self.out.close()
        with open(self.path) as f:
            self.stalls = [tuple(map(float, line.split())) for line in f if line.strip()]
        return self.stalls

    def worst(self, a, b):
        """The latest the host ran a tick in [a, b], in seconds (0 when on
        time); the stretch of [a, b] before the probe ran counts as late by its
        length."""
        unseen = min(b, self.started) - a if a < self.started else 0.0
        return max([unseen] + [d for t, d in self.stalls if t < b and t + d > a])


def header(book, size, tier, seed=None):
    """The replay header of a `--book B --no-title` session: `--seed N`
    starts the generated page (start 0), no seed the book's first preset."""
    start = (0 if seed is not None else 1)
    start = start if book == 1 else 10000 + book * 2000 + start
    return 'pk 1\nseed %d\ntier %s\nsize %s\nstart %d\n' % (7 if seed is None else seed, tier, size, start)


def applied(binary, scratch, data, size):
    """(glyphs, styles) of terminal bytes through the game's terminal model."""
    import subprocess
    path = os.path.join(str(scratch), 'paced-apply.bin')
    with open(path, 'wb') as f:
        f.write(data)
    r = subprocess.run([binary, '--apply', path, '--size', size], capture_output=True, timeout=60)
    if r.returncode:
        return None
    text, styles, _ = r.stdout.decode().split('--\n')
    return text, styles


def replayed(binary, scratch, head, keys, size, frames=2):
    """(glyphs, styles) of the headless replay of `keys`, all at tick 1."""
    import shutil, subprocess
    script = os.path.join(str(scratch), 'paced-expected.pk')
    dest = os.path.join(str(scratch), 'paced-expected')
    with open(script, 'w') as f:
        f.write(head + ''.join('t 1 %s\n' % k for k in keys))
    if os.path.exists(dest):
        shutil.rmtree(dest)
    subprocess.run([binary, '--headless', '--script', script, '--size', size, '--frames', str(frames),
                    '--every', str(frames), '--dump', dest, '--mute'], check=True, capture_output=True, timeout=60)
    return (open(os.path.join(dest, 'final.txt'), encoding='utf-8').read(),
            open(os.path.join(dest, 'final.sty'), encoding='utf-8').read())


def await_state(s, binary, scratch, want, size, what, bound=LIVENESS_S):
    """A session whose stderr shares the terminal cannot carry --trace: its
    acknowledgement is the exact replayed state (every glyph and style),
    awaited with a liveness bound. Returns the bytes that reached it."""
    deadline = time.monotonic() + bound
    while True:
        data = s.out
        if applied(binary, scratch, data, size) == want:
            return data
        if time.monotonic() >= deadline:
            raise AssertionError('STATE: %s never drew its exact replayed frame within %.0f s' % (what, bound))
        s.pump(.02)


def carrying_frames(keys, carrying):
    """{frame: [(index, record tick, key)]}: each key in the first carrying frame after its tick."""
    by = {}
    for i, (t, k) in enumerate(keys):
        f = next((c for c in carrying if c > t), None)
        if f is not None:
            by.setdefault(f, []).append((i, t, k))
    return by


def redrive(name, attempt, problems, bound=REDRIVES):
    """attempt(n) for n = 1.. until it does not raise Unrealised; at most `bound`
    sessions, each re-drive printed; never realised is SCHEDULE."""
    why = None
    for n in range(1, bound + 1):
        try:
            return attempt(n)
        except Unrealised as e:
            why = e
            print('%s: session %d out of its case (%s)%s' % (name, n, e, '; driven again' if n < bound else ''), flush=True)
    problems.append('%s: SCHEDULE: the case was never realised in %d sessions (%s)' % (name, bound, why))
    return None
