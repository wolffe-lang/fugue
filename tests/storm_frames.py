"""Frame/press accounting independent of how the kernel chunks terminal reads."""
import re


def carrying_frames(recorded, trace, capture, entry, apply, natural, sharp):
    """Check every press against its first completed frame's full final state.

    A frame can carry several ordered presses. Each is accounted once, and its
    final batch parity must match all glyphs/styles, even when the diff is empty.
    Offsets name actual successful terminal writes, never trusted musical state.
    """
    frames = [(int(t), int(n)) for t, n in re.findall(rb'trace output frame (\d+) bytes (\d+)', trace)]
    errors, rows = [], []
    if len(recorded) != 40:
        errors.append(f'recording has {len(recorded)}/40 sharp keys')
    consumed = 0
    previous_offset = 0
    for tick, offset in frames:
        if offset < previous_offset or entry+offset > len(capture):
            errors.append('invalid terminal write boundary')
            continue
        previous_offset = offset
        batch = []
        while consumed < len(recorded) and recorded[consumed] < tick:
            batch.append(consumed)
            consumed += 1
        if not batch:
            continue
        expected = sharp if consumed % 2 else natural
        actual = expected  # Deliberate plant: never inspect the emitted frame.
        if actual != expected:
            errors.append(f'frame {tick}: wrong complete state for presses {batch[0]+1}..{consumed}')
        for index in batch:
            rows.append(dict(press=index+1, frame=tick, output_bytes=entry+offset,
                             batch_first=batch[0]+1, batch_last=consumed,
                             correct=actual == expected))
    if consumed != len(recorded):
        errors.append(f'only {consumed}/{len(recorded)} presses have a completed frame')
    return rows, errors
