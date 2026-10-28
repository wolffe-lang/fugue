"""The forty-press claim survives batching, but never a missing state."""
from pathlib import Path
import runpy
import unittest
import threading
import time

helpers = runpy.run_path(str(Path(__file__).with_name('storm_frames.py')))
check = helpers['carrying_frames']

class OwnerObserver(unittest.TestCase):
    def test_blocked_process_poll_cannot_block_forty_key_deliveries(self):
        entered=threading.Event();release=threading.Event();returned=threading.Event()
        def blocked():
            entered.set();release.wait();return [123]
        sampler=helpers['ChildSampler'](blocked,time.monotonic())
        def begin():
            sampler.begin();returned.set()
        caller=threading.Thread(target=begin)
        caller.start()
        try:
            self.assertTrue(entered.wait(2))
            self.assertTrue(returned.wait(2),'owner polling blocked its caller')
            sent=[]
            for index in range(40):sent.append(index)
            self.assertEqual(len(sent),40)
            self.assertTrue(sampler.thread.is_alive())
            self.assertEqual(sampler.polls,[])
        finally:
            sampler.stop.set();release.set();caller.join()
            if sampler.thread.ident is not None:sampler.finish()
        self.assertEqual(sampler.polls[0]['pids'],[123])
        self.assertFalse(sampler.thread.is_alive())

    def test_owner_sampler_never_hides_a_real_overlap(self):
        entered=threading.Event()
        def overlap():
            entered.set();return [123,456]
        sampler=helpers['ChildSampler'](overlap,time.monotonic())
        sampler.begin()
        try:self.assertTrue(entered.wait(2))
        finally:sampler.finish()
        self.assertEqual(sampler.polls[0]['pids'],[123,456])
        self.assertEqual(sampler.errors,[])

class StormFrames(unittest.TestCase):
    def run_frames(self, capture=b'SN'*20, width=1, offsets=None):
        ticks = [i//width for i in range(40)]
        if offsets is None:
            offsets = [(i+1)*width for i in range(40//width)]
        trace = b''.join(f'trace output frame {i+1} bytes {n}\n'.encode() for i,n in enumerate(offsets))
        return check(ticks, trace, capture, 0, lambda b:b[-1:] or b'N', b'N', b'S')

    def test_forty_separate_frames(self):
        rows, errors = self.run_frames()
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 40)

    def test_coalesced_terminal_read_keeps_forty_frames(self):
        rows, errors = self.run_frames()
        self.assertEqual(sum(r['correct'] for r in rows), 40)
        self.assertEqual(errors, [])

    def test_twenty_two_press_batches_still_account_forty(self):
        rows, errors = self.run_frames(b'', 2, [0]*20)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 40)
        self.assertTrue(all(r['batch_last']-r['batch_first'] == 1 for r in rows))

    def test_dropped_press_frame_cannot_pass(self):
        capture = b'SN'*20
        capture = capture[:10] + b'N' + capture[11:]
        rows, errors = self.run_frames(capture)
        self.assertTrue(errors)
        self.assertFalse(rows[10]['correct'])

    def test_last_frame_cannot_hide_missing_intermediate(self):
        _, errors = self.run_frames(b'N'*40)
        self.assertTrue(errors)

    def test_missing_boundary_is_not_a_completed_press(self):
        _, errors = self.run_frames(offsets=list(range(1,40)))
        self.assertIn('only 39/40 presses have a completed frame', errors)

if __name__ == '__main__': unittest.main(verbosity=2)
