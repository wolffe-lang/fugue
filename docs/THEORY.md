# Theory

Six modes use the white keys, with finals C, D, E, F, G and A. A pitch has a
letter, octave and accidental; intervals retain spelling as well as semitones.
Unisons, fifths and octaves are perfect consonances. Major/minor thirds and
sixths are imperfect consonances. All others, including fourths, are dissonant.

## The cantus

Write eight to sixteen notes, beginning and ending on the final. Approach the
last note by a step from above, or the leading semitone below; Dorian,
Mixolydian and Aeolian may raise that seventh at the cadence. Keep every other
note diatonic. One highest note stands at least three notes from either end,
never on the leading tone. Use two to four leaps, mostly steps. A leap wider
than a third must turn back by one step. Never leap twice in the same direction.
No sevenths, altered intervals or leaps beyond the octave; at most one octave.
Do not outline a tritone across three or four notes, repeat a note, or repeat
a two- or three-note figure immediately at a new height. Stay within a tenth,
turn at least twice and balance rising and falling motions.

For a reproducible judge, balance means the counts of rising and falling
motions differ by at most three. Sequence means two adjacent equal-length
blocks with identical diatonic interval patterns, including literal repeats.
These are explicit game conventions, not claims that every historical teacher
used the same test. The six cited Fux lines are oracles only; none passes every
one of these stricter conventions. Their exact named breaks are pinned in tests.

The seeded generator enumerates pruned ten-note candidates inside a tenth,
with a 200,000-prefix ceiling and up to 64 candidates per mode. It ranks the
pool by summit placement and interval variety, then the seed chooses among
the best sixteen. A census exercises fifty seeds in each mode. A seed is not
a promise that no other seed shares the same line.


## First species

Place a consonance at every bar. Above a lower cantus, open with a perfect fifth
or octave. Below an upper cantus, open with a unison or octave. Close on a unison
or octave, both voices approaching by step: a minor third contracts to unison,
or a major sixth expands to the octave. Use the raised leading tone where the
mode needs it. Phrygian keeps its characteristic semitone in the cantus instead.

Never carry perfect fifths, octaves or unisons in parallel. Do not approach a
perfect interval with both voices moving the same way, even when the earlier
interval was imperfect: this is the hidden-perfect rule. Do not cross the
voices, step beyond the other voice's previous note, or meet at a unison inside
the phrase. Your own melody follows the cantus's melodic rules; its beginning
and ending are governed by these two-voice rules instead of the cantus's tonic
endpoint requirement. The critic identifies each break by its one-based bar.

## Stars

No stars are awarded to an illegal answer. A legal answer earns one star, two
when at least three goals are met, and three when all five are met:

- At least 50% of transitions move in contrary motion.
- At least 60% of your melodic transitions are steps.
- Your one highest note occurs at a different bar from the cantus's highest note.
- No chain of parallel thirds or sixths exceeds three bars.
- At least three different simple interval numbers occur.

The card shows the actual shares, booleans and interval count. The measures do
not disguise hard errors inside an averaged number. A seeded exercise is proved
to admit a legal answer before it is offered, but not every seed is guaranteed
to admit a three-star one. The three tutorial reference solutions do.

## Historical test lines

The only borrowed music is the six cantus firmi transcribed in
`tests/oracles/fux.txt`, from Fux's public-domain *Gradus ad Parnassum* (Vienna,
1725), printed pages 47, 51, 52, 53, 55 and 62. The original scan is
https://archive.org/details/gradusadparnassu00fuxj_0 . Their exact named breaks
are expected test results, not errors suppressed to make the historical examples
fit. No Fux line or counterpoint appears in a playable level.


## Reading the shared staff

The named staff is a diatonic pitch-space viewport, not a fixed treble or bass
clef. Position 28 is C4; each row upward is the next letter, and an accidental
shares that letter's row. All six modes use this white-key step series; a
mode changes its final, not the meaning of a pitch name. The lower line is two
steps above the bottom pitch of the current viewport. Lines are two steps
apart, with one intervening space each. Every viewport row is named, including
spaces and ledger positions; C4 is bold.

For bottom C4, the lines are exactly the conventional treble E4 G4 B4 D5 F5,
and the spaces are F4 A4 C5 E5. In a lower register the named lines move with
the viewport so all five remain visible; they do not silently retain treble
names. The optional spiral art study is not a treble clef. This shared space
makes the interval between both voices readable without a second staff.
`test_pitch_row_margin_round_trip_whole_viewport` holds names, C4, line/space
steps, ledger continuation and both mapping directions to the same convention.
