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
## Second species: two against one

The given voice still holds whole notes. Write two halves in each bar, then a
whole at the end. The first half may be a rest. Every downbeat is consonant;
save a downbeat unison for the beginning or end. On a weak half, a dissonance
must be a passing note: step into it and step out in the same direction. A
returning neighbour is not allowed in this book.

The last weak half makes the same major-sixth-to-octave or
minor-third-to-unison close as Book I. The critic checks perfect parallels
between successive sounding notes and between downbeats: a busy weak beat
cannot disguise two strong fifths moving together. Crossing, overlap, hidden
perfects and the melodic canon still apply.

## Third species: four against one

Write four quarters against each whole, with a final whole. Strong beats remain
consonant. A weak dissonance can pass through by step or return by step to the
note it left. Two passing quarters can connect consonant endpoints in three
steps, all in one direction.

The cambiata is a complete five-note turn. Above the given voice, step down
from a consonance to a dissonance, leap down a third onto a consonance, then
return by two upward steps. The lower voice uses the mirrored figure. The
first four notes are quarters beginning on a downbeat; the fifth belongs to
the next bar. All notes except the second must be consonant against the given
voice sounding at their own time. An unfinished fragment earns no exemption.

Perfect parallels are checked between adjacent notes, between downbeats, and
between the same quarter positions in adjacent bars. Close by step from the
last weak consonance, as in the earlier books.

## Fourth species: the suspended voice

Begin with a half rest and a consonant half, or strike an allowed opening
perfect interval. Carry a half-note pitch across the barline with a tie. If
it rubs against the new cantus note, prepare it as a consonance on the previous
weak half and resolve it downward by one step on the next weak half.

Above the given voice, the allowed dissonant suspensions are 7–6 and 4–3.
A ninth may resolve to an octave (9–8), but a second may not resolve to a
unison above. Below the given voice, use 2–3. Altered intervals do not qualify.
A repeated attack is not a tie, and a tie cannot change pitch or spelling.

Where a suspension cannot work, break the chain with consonances; the ordinary
motion rules still apply. In the penultimate bar use 7–6 above or 2–3 below,
then step into the final octave or unison. The critic checks both the suspended
figure and the final two-voice cadence.

## Fifth species: the florid voice

Mix whole, half and quarter notes. Eighths come in pairs on a weak quarter
(the second or fourth quarter of a bar), with a step into, through and out of
the pair. Do not place a lone eighth or an eighth pair on the downbeat. A weak
dissonance still needs its passing or neighbour figure; a downbeat dissonance
still needs a complete suspension. A cambiata keeps its four-quarter shape.
The judge names the figure it recognizes rather than accepting dissonance
merely because this is the freer book.

Florid style adds two visible goals: use at least three note values, and let
tied continuations occupy at least ten percent of sounding time. All seven
goals give three stars. A legal line with three goals gives two; other legal
lines give one. These are game style goals, not historical laws.

## Melody and rhythm

The eight-to-sixteen-note length requirement describes the cantus's bars, not
the number of attacks in a faster counterpoint. Apply the remaining melodic
canon to the full attack line: rests do not count, and a tied continuation is
not a fresh attack. Use at least two leaps, with an upper allowance of four per ten attacks,
rounded up (never an upper allowance below two). Faster species have more
attacks, so this scales the same preference for steps rather than making a
longer voice artificially leap-free. Book I retains its two-to-four bound.
The critic reports the containing bar when a melodic attack breaks a rule.
Contrary-motion percentage counts simultaneous moving attacks across a cantus
change; tied and oblique boundaries are not opportunities for contrary motion.
Step percentage counts melodic attacks. Holding a cantus note through four
quarters does not manufacture three failed opportunities for contrary motion.

Below an upper cantus, a minor tenth may contract to an octave: it is the
minor-third close with the lower voice displaced by one octave. In Aeolian,
the sixth may be raised only immediately before the raised seventh in the
final stepwise ascent (F-sharp, G-sharp, A). This supplies the fifth–sixth–octave
cadence without allowing an augmented second or excusing accented parallels.
No other chromatic alteration is admitted by that exception.
