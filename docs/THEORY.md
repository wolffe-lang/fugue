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

The treble's lines are E4 G4 B4 D5 F5; its spaces F4 A4 C5 E5. The bass's
lines are G2 B2 D3 F3 A3; its spaces A2 C3 E3 G3. Position 28 is C4.
Accidentals share their letter's row, but retain spelling for intervals and
sound. The viewport can scroll without changing a line's pitch.

A page with a lowest initial pitch at or above G3 chooses treble, otherwise
bass. More than three ledgers on either side chooses a treble-over-bass system;
each voice uses the clef selected by its initial range. A ledger between the
staves stops at middle C's shared ledger. Clefs stay fixed while editing.

The drawn head, margin name, interval and synthesized note all use the same
stored spelled pitch. Screen rows never feed the harmonic calculation. The
editor permits C1–B6 in Books I–V; the judge, not a modal register clamp,
reports range and crossing errors. Pages can supply a different sounding range.

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

## Editing florid time

Book V's starting rhythm is a suggestion, not a locked answer. Split, join,
dot, outgoing tie and rest edits are reversible. Values are integer eighths:
1, 2, 3, 4, 6 or 8; 3 and 6 denote dotted quarters and halves. A dot borrows
from the following event, so every bar still totals eight. The same figure
classifier and melodic checker judge the edited line. An interior rest, an
unprepared tie or an unpaired eighth remains a named error, not an editor ban.

## Sixth book: the fugue

A subject is a small musical thought with a recognizable head and a stepping
last three notes. Keep it in its mode, within a ninth, for four to eight bars.
Begin on the final or fifth and leave on either of those degrees. A leap or a
turning step figure marks the head. At least sixty percent of its motions are
steps. The melodic rules from Book I still apply: one summit, balanced motion,
recovered wide leaps, no altered leaps, repeats, sequences or outlined tritones.
The length now counts bars, not attacks. This book's subjects strike each note;
they have no rests or tied repetitions. Values come from the florid grid;
eighths, when used, must be weak pairs moving by step.

The generator writes ten attacks in six bars, mixing quarters, halves and
wholes. It enumerates at most 200,000 prefixes for each opening degree, keeps
up to thirty-two valid lines from each, and the seed selects one. The three
tutorial subjects are original, explicitly written lines. None comes from a
published fugue. Every generated subject is checked by the same named rules.

### Answer the head

The answer enters after the subject. When the subject is the lower voice,
answer a perfect fifth above; when it is the upper voice, answer a perfect
fourth below. A **real answer** preserves every spelled interval and every
value exactly. Transposition may introduce an accidental: B becomes F-sharp
at the fifth above. This is not a wrong note simply because the subject used
only white keys.

A **tonal answer** makes one exchange at the head. If the subject begins on
the fifth degree, that first attack answers on the tonic. If it begins with
final then fifth, the second attack answers on the tonic. This is one diatonic
step below the corresponding real answer; everything after it remains exact.
For a C subject beginning C–G, the real answer begins G–D, while the tonal
answer begins G–C. For a subject beginning G, the real answer begins D and
the tonal answer begins C. The octave follows the chosen upper or lower entry.
Other heads have a real answer only. The head shape is not enough: the mutation
must also preserve the melodic rules, with the open endpoints allowed here.
For example, G–B in a C subject gives the real D–F-sharp; mutating it to
C–F-sharp creates an augmented fourth and is refused by name. C–G–F would
become G–C–C, so that repeated note makes it real-only too. Where the exchange
remains melodic, either form is allowed: the card names **Real answer** or **Tonal answer**, and names
the mutation's attack and bar. A mutation elsewhere is a wrong transposition,
reported at its bar, not an alternative interpretation.

### Continue, then exchange places

The first voice continues as the countersubject while the answer enters.
Write florid counterpoint against the answer's actual moving notes. A note
held across an answer attack is still checked; passing notes, neighbours,
cambiatas, weak paired eighths and prepared suspensions keep their complete
figures. Crossing, overlap, hidden and parallel perfect intervals remain
forbidden, including equal beats in adjacent bars.

The countersubject must work **both ways up at the octave**. The judge first
places it above the answer, then lowers it exactly an octave and checks the
whole pair again. Keep their span within an octave. Thirds become sixths;
sixths become thirds. A perfect fifth becomes a fourth against the new bass:
the critic calls this **inversion-fifth**, rather than saying vaguely that the
second version sounds wrong. This book excludes those fifths even on weak
beats. Errors found only after the exchange have an `inverted-` name.

These are entries, not closed cantus exercises. Their melodic and florid rules
remain, but neither voice must end on the original tonic or make Book V's
sixth-to-octave closing cadence. For example, a C subject ending on G can have
a real answer ending on D; a consonant counterpoint there leaves the exposition
open without being an unfinished cadence exercise. A third subject entry and
a final closing cadence are not part of these pages.

### The last pages and their stars

The first tutorial asks for the answer, with the first voice's continuation
already written. The second supplies the subject and real answer and asks
for the countersubject. The third asks for both. On that page and seeded pages,
`v` changes the writing desk without losing either voice. Undo belongs to the
current desk; switching starts a new undo history. `h` plays the subject alone,
then the answer and countersubject together, naming the entries as they sound.
After all three tutorials pass, the end card counts the three pieces and their
stars, and the sixth book lights on the title. Seeded pages follow.

Stars return to the five melodic and harmonic goals: contrary motion at least
fifty percent, steps at least sixty percent, separate climaxes, no run longer
than three parallel thirds or sixths, and at least three interval classes.
All five give three stars, three give two, and other legal answers give one.
Both answer and inversion checks must pass first. Unlike Book V, this book
does not ask for a proportion of tied notes: the answer must copy a subject's
exact attacks, and these short subjects have no ties. Rhythm stays a hard
musical check, not a reward for changing the given subject.

A seeded page is offered only after a separate bounded search finds a legal
invertible countersubject. That search tries the answer's rhythm, thirds and
sixths, with unisons or octaves at the edges, for at most 30,000 prefixes.
It does not explore every florid rhythm. A search miss is not proof that the
subject has no good counterpoint; it is skipped, never admitted under weaker
rules. The seed may share a page with another seed, and three stars are not
promised for every admitted page.
