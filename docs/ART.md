# The manuscript

The page is a piece of warm parchment, with a low-density grain driven by the
engine's seeded world noise and cell hash. Its ground is never a flat fill.
The initial F is drawn from an original cell mask: blue ink within a quiet
sepia frame. No font, image, sprite sheet or other game's drawing is bundled.

A shared five-line staff keeps both voices in the same pitch space. Each line
and space takes one cell row. Bars are fixed-width columns; a hollow sepia
circle is the cantus, and a filled dark-blue circle is the player's note, offset
one cell so unisons remain visible. Ledger lines extend the staff as needed.
Interval labels below the notes carry both quality/number and consonance colour.
The right margin points to the first broken rule by bar; Enter opens the full
scrollable critic's card. During listening, one column lights per second.

At 80x24 the page is compact; 120x40 adds breathing room without stretching
pitch spacing. Notes outside a deliberately edited wide register are marked
with ^/v at the viewport edge instead of silently disappearing. The same marks,
positions and line lengths are used on plain, with o and * replacing circles.

## Names or a drawn clef

Pitch names are the default. The alternative cell-drawn clef is an art study,
not a second input convention. Compare `tests/goldens/art/names-80-plain.txt`
and `clef-80-plain.txt`; the rich versions and both 120-column versions are
beside them. Names make the absolute pitch immediately readable on plain,
where the drawn clef is only a small spiral. C4 is distinguished with bold ink
when it is in the viewport. The names are therefore the recommended treatment.

Every golden has a companion `.sty` file: colour and attributes are part of the
image, not a promise inferred from an uncoloured text capture.
