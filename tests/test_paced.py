"""tests/paced.py's rows: key cutting, the carrying-frame map, the trace parser,
the acknowledgement check, and the whole protocol against a stand-in game.

The stand-in (FAKE below) follows the rules of src/fugue.lu's live loop that
the injector relies on, in a real pty: it reads at most 256 bytes when it
wakes, applies every key it read on the wake's first due tick, steps every due
tick and draws once, then prints `trace output frame` and `carries_key`. It
can be told to stall (sleep) before chosen ticks, so its next wake catches up
several ticks and reads two writes in one frame, as a loaded runner does.
Run by tests/test_storm_frames.py (which tools/check runs) and alone.
"""
from pathlib import Path
import os
import pty
import runpy
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

P = runpy.run_path(str(Path(__file__).with_name('paced.py')))
# Scratch inside the checkout (gitignored target/), never the system's temp.
SCRATCH = Path(__file__).resolve().parents[1] / 'target' / 'test-paced'

# fugue#36's second red attempt (41344575553, attempt 2, 0-120-plain-sound):
# the recorded ticks of its first five presses and the frames that carried them.
ATTEMPT_2_KEYS = [(5, 'new'), (5, 'new'), (6, 'right'), (13, 'left'), (19, 'right'), (21, 'right'), (21, 'right'), (22, 'right')]
ATTEMPT_2_CARRYING = [6, 7, 14, 21, 22, 23]


class Keys(unittest.TestCase):
    def test_keys_are_cut_whole(self):
        data = b'\x1b[C\x1b[D' + b'\x1bOA' + b'\x1b[1;2:3A' + b'\x1b[104;1:1u' + b'r[.' + b'\x1b'
        self.assertEqual(P['keys_of'](data), [b'\x1b[C', b'\x1b[D', b'\x1bOA', b'\x1b[1;2:3A', b'\x1b[104;1:1u',
                                              b'r', b'[', b'.', b'\x1b'])

    def test_pieces_never_split_a_key_and_fit_one_read(self):
        data = b'\x1b[C' * 100 + b'\x1b[A' * 100
        pieces = P['pieces'](data)
        self.assertEqual(b''.join(pieces), data)
        self.assertTrue(all(len(p) <= P['READ_MAX'] for p in pieces))
        self.assertTrue(all(len(p) % 3 == 0 for p in pieces))
        self.assertEqual(len(pieces), 3)


class CarryingFrames(unittest.TestCase):
    def test_a_catch_up_frame_carries_the_key_trunk_left_unaccounted(self):
        by = P['carrying_frames'](ATTEMPT_2_KEYS, ATTEMPT_2_CARRYING)
        # The key recorded at 19 is drawn at 21, beside nothing else.
        self.assertEqual([k for _, t, k in by[21]], ['right'])
        self.assertEqual([t for _, t, _ in by[22]], [21, 21])
        self.assertEqual(sum(len(v) for v in by.values()), len(ATTEMPT_2_KEYS))
        # trunk's rule (a key at T only in the frame traced at T+1) loses it.
        trunk = {f: [k for t, k in ATTEMPT_2_KEYS if t == f - 1] for f in ATTEMPT_2_CARRYING}
        self.assertEqual(sum(len(v) for v in trunk.values()), len(ATTEMPT_2_KEYS) - 1)


class Stub:
    """A Session base that starts nothing: the parser and verify alone."""
    def __init__(self, argv, rows, cols, env, settle=0.0, replies=()):
        self.out, self.err, self.eof, self.replies, self.reply_times = b'', b'', False, list(replies), []


class Ctx:
    Session = Stub


class Verify(unittest.TestCase):
    def session(self, err, out=b''):
        s = P['session'](Ctx)(['game', '--trace'], 24, 80, {})
        s.err = err
        s.out = out
        s._parse()
        return s

    def test_parser_reads_whole_lines_once(self):
        s = self.session(b'trace output frame 7 bytes 10\nsound: x\ntrace frame 7 carries_key inner_us 5\ntrace output fr')
        self.assertEqual([(t, n) for t, n, _, _ in s.outputs], [(7, 10)])
        self.assertEqual([(t, u) for t, u, _, _ in s.carrying], [(7, 5)])
        s.err += b'ame 8 bytes 12\n'
        s._parse()
        self.assertEqual([(t, n) for t, n, _, _ in s.outputs], [(7, 10), (8, 12)])

    def record(self, keys):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        f = tempfile.NamedTemporaryFile('w', suffix='.pk', delete=False, dir=SCRATCH)
        f.write('pk 1\n' + ''.join('t %d %s\n' % k for k in keys))
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def acked(self, frames):
        err = b''.join(b'trace output frame %d bytes 0\ntrace frame %d carries_key inner_us 1\n' % (f, f) for f in frames)
        s = self.session(err, P['QUERY'] + P['LEAVE'])
        s.acks = [{'frame': f, 'carried': [f], 'single': True} for f in frames]
        return s

    def test_acks_agreeing_with_the_recording_pass(self):
        s = self.acked([6, 8, 11])
        problems = []
        s.verify(self.record([(5, 'right'), (7, 'right'), (9, 'left')]), 'case', problems)
        self.assertEqual(problems, [])

    def test_an_ack_read_off_by_one_is_red_by_name(self):
        s = self.acked([6, 8, 11])
        s.acks[1]['frame'] = 7; s.acks[1]['carried'] = [7]
        problems = []
        s.verify(self.record([(5, 'right'), (7, 'right'), (9, 'left')]), 'case', problems)
        self.assertTrue(any('ACK:' in p for p in problems), problems)

    def test_a_key_the_recording_never_acknowledged_is_red(self):
        s = self.acked([6, 11])
        problems = []
        s.verify(self.record([(5, 'right'), (7, 'right'), (9, 'left')]), 'case', problems)
        self.assertTrue(any('ACK:' in p for p in problems), problems)


FAKE = r'''
import os, select, sys, time, tty
tty.setraw(0)
stalls = {int(t): float(s) for t, s in (w.split(':') for w in sys.argv[1].split(',') if w)}
record = open(sys.argv[2], 'w')
TICK = 1 / 30
start = time.monotonic(); tick = 0; pending = []; applied = 0; written = 0; stalled = set()
os.write(1, b'\x1b[?1049h\x1b[?25l\x1b[H\x1b[2J\x1b[?u')
while True:
    due_at = start + (tick + 1) * TICK
    ready, _, _ = select.select([0], [], [], max(0.0, due_at - time.monotonic()))
    if ready:
        data = os.read(0, 256)
        pending += [b for b in data]
    due = 0
    while time.monotonic() >= start + (tick + due + 1) * TICK:
        due += 1
    if due == 0:
        continue
    quit = False
    for b in pending:
        if b == ord('q'): quit = True
        else: applied += 1
        record.write('t %d %s\n' % (tick, 'quit' if b == ord('q') else 'key'))
    carries = bool(pending); pending = []
    tick += due
    frame = ('\x1b[1;1H%05d' % applied).encode()
    os.write(1, frame); written += len(frame)
    sys.stderr.write('trace output frame %d bytes %d\n' % (tick, written))
    if carries:
        sys.stderr.write('trace frame %d carries_key inner_us 1\n' % tick)
    sys.stderr.flush()
    if quit:
        break
    for t in [t for t in stalls if t <= tick and t not in stalled]:
        stalled.add(t); time.sleep(stalls[t])
record.close()
os.write(1, b'\x1b[0m\x1b[?25h\x1b[?1049l')
'''


class Pty:
    """A minimal pty session for the stand-in (lair's Session's shape)."""
    def __init__(self, argv, rows, cols, env, settle=0.0, replies=()):
        self.master, slave = pty.openpty()
        r_err, w_err = os.pipe()
        self.proc = subprocess.Popen(argv, stdin=slave, stdout=slave, stderr=w_err, close_fds=True)
        os.close(slave); os.close(w_err)
        self.r_err = r_err
        self.out, self.err, self.eof, self.replies, self.reply_times = b'', b'', False, list(replies), []
        self.pump(settle)

    def type(self, data, settle=0.08):
        os.write(self.master, data)
        self.pump(settle)

    def finish(self):
        deadline = time.monotonic() + 10
        while self.proc.poll() is None and time.monotonic() < deadline:
            self.pump(.01)
        self.proc.wait(timeout=10)
        self.pump(.05)
        os.close(self.master); os.close(self.r_err)


class PtyCtx:
    Session = Pty


class Protocol(unittest.TestCase):
    """The whole protocol against the stand-in, unloaded and with catch-up stalls."""

    def run_game(self, stalls, drive):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        d = tempfile.mkdtemp(prefix='game-', dir=SCRATCH)
        self.addCleanup(shutil.rmtree, d, True)
        record = os.path.join(d, 'record.pk')
        script = os.path.join(d, 'fake.py')
        Path(script).write_text(FAKE)
        s = P['session'](PtyCtx)([sys.executable, '-I', script, stalls, record, '--trace'], 24, 80, {})
        s.ready()
        drive(s)
        s.type(b'q', 0); s.finish()
        problems = []
        keys = s.verify(record, 'fake', problems)
        self.record = record
        return s, keys, problems

    def count(self, s, ack):
        return int(s.frame(ack['frame'])[-5:])

    def test_one_key_a_tick_is_acknowledged_by_its_own_frame(self):
        acks = []
        s, keys, problems = self.run_game('', lambda s: acks.extend(s.burst(b'k', 12)))
        self.assertEqual(problems, [])
        self.assertEqual([self.count(s, a) for a in acks], list(range(1, 13)))
        self.assertEqual(len(keys), 13)

    def test_a_stalled_wake_catches_up_and_every_ack_is_still_exact(self):
        acks = []
        s, keys, problems = self.run_game('8:0.2,20:0.15', lambda s: acks.extend(s.burst(b'k', 20)))
        self.assertEqual(problems, [])
        self.assertEqual([self.count(s, a) for a in acks], list(range(1, 21)))
        self.assertGreater(max(s.lateness()), 1)
        ticks = [t for t, _, _, _ in s.outputs]
        self.assertTrue(any(b - a > 1 for a, b in zip(ticks, ticks[1:])), 'no catch-up wake was forced')

    def test_a_batch_is_acknowledged_once_all_of_it_is_applied(self):
        acks = []
        def drive(s):
            acks.append(s.send(b'k' * 300))
            acks.append(s.send(b'k'))
        s, keys, problems = self.run_game('3:0.2', drive)
        self.assertEqual(problems, [])
        self.assertEqual(self.count(s, acks[0]), 300)
        self.assertEqual(self.count(s, acks[1]), 301)

    def test_a_scheduled_stream_a_stall_coalesces_is_acknowledged_whole(self):
        acks = []
        def drive(s):
            start = s.tick + 1
            first = s.write_at(b'k', start)
            for i in range(1, 30):
                s.write_at(b'k', start + (3 * i) // 2)
            acks.append(s.settle(first))
        s, keys, problems = self.run_game('10:0.25', drive)
        self.assertEqual(problems, [])
        self.assertEqual(self.count(s, acks[0]), 30)
        by = P['carrying_frames'](keys, [c[0] for c in s.carrying])
        self.assertTrue(any(len(v) > 1 for v in by.values()), 'the stall coalesced no presses')

    def test_a_tick_read_off_by_one_is_red(self):
        acks = []
        s, keys, problems = self.run_game('', lambda s: acks.extend(s.burst(b'k', 5)))
        self.assertEqual(problems, [])
        for a in s.acks:
            a['frame'] -= 1
            a['carried'] = [a['frame']]
        problems = []
        s.verify(self.record, 'fake', problems)
        self.assertTrue(any('ACK:' in p for p in problems), problems)

if __name__ == '__main__':
    unittest.main(verbosity=2)
