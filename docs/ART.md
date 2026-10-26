# The manuscript

The page is a piece of warm parchment, with a low-density grain driven by the
engine's seeded world noise and cell hash. Its ground is never a flat fill.
The initial F is drawn from an original cell mask: blue ink within a quiet
sepia frame. No font, image, sprite sheet or other game's drawing is bundled.

A shared five-line staff keeps both voices in the same pitch space. Each line
and space takes one cell row. Five continuous runs of `─` (plain `-`) span the
staff; `│` (plain `|`) crosses them at bar boundaries. The four intervening
spaces retain only the parchment grain. Three-cell ledgers extend beyond the
five lines only where a note needs them. There are no underscore staff marks.
The pitch viewport scrolls over fixed clefs: treble E4 G4 B4 D5 F5 or
bass G2 B2 D3 F3 A3. The page chooses treble when its initial lowest pitch
is G3 or higher, bass otherwise. Editing never changes those line names.
Pitch names label every visible line and space; C4 is bold.

A page needing more than three ledgers uses a grand staff: treble above bass,
labelled Tr and Ba at the margin. Each voice retains its page-selected staff;
the two staves share one continuous pitch map and middle C's ledger. At 80x24
this spends the title/header space on 21 pitch rows; intervals occupy row 22
and the hint row 23. At 120x40 the system has breathing room. A very wide edit
scrolls the map and marks notes outside it with ^/v; it never relabels a line.

The cantus keeps its hollow circle (`○`, plain `o`) and is bold deep red:
xterm 52 (#5f0000), against the player's blue 24. Its measured contrast is
13.815:1 on parchment 230, 10.488:1 on grain 223 and 10.307:1 on sounding
222. Plain uses bright red 9 versus blue 4 on 7; console colours are
theme-dependent, so no RGB contrast claim is made for a user's plain palette.
Symbols do not change with colour. Sharps/flats are spelled beside the head;
a selected natural has an explicit natural sign. Adjacent heads and barlines
are never overwritten by an accidental.

The panel follows the selected event: **Bar N, beat B:8**, the interval and its
class, the figure allowed at that beat, and named local findings at that event. The
separately titled **Breaks: bar N** list contains only findings in the active bar.
Every finding row names its bar; Enter still opens the global critic card.
The harmonic class and figure are separate: a passing dissonance remains
labelled dissonant even when its figure is allowed.

## Content-sized measures

A measure costs one barline column plus the sum of its event widths. An event
uses the maximum of its value minimum, its pitch-name width plus one, and its
strong/weak interval-label width plus one. Tuned minima are whole 6, half 5,
quarter 4 and eighth 4; the eighth's flag, three-cell ledger and label need
four cells. Dotted halves use 5, dotted quarters 4. Editable held values reserve at least
one cell per eighth (a whole therefore needs eight cells, a dotted half six).
The extra label cell keeps
neighbouring labels separate. Drawing stops only at a complete event boundary;
a partially shown bar keeps its number, and `>>` marks the cut. Moving right
scrolls whole bars until the complete selected event fits.

Interval labels sit one row below the lowest note, ledger, staff line or tie
in their column. Value labels follow when there is room. The caret advances one cell per
editable unit inside a held event; a selected head still identifies the note
that Up/Down will change. On the compact grand staff the caret uses the
bar-number row, leaving the interval and permanent hint intact. Layout is
recomputed on every pitch, rhythm and cursor change. Stems and shallow tie arcs
are original cell drawings, not borrowed notation assets.

Every golden has a companion `.sty` file: colour and attributes are part of the
image, not a promise inferred from an uncoloured text capture.



Book VI uses the common selected-event column: bar and beat at the top,
interval, pitch and figure beneath, then the active bar's named findings.
Its voice-entry names stay in the header rather than over these diagnostics.
The sparse ground-223 cells are deliberate parchment grain, recorded in the
style goldens even where the text capture contains a space. Whole-cell pty
comparisons check both glyphs and styles after page changes and playback.
