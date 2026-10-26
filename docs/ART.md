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
The pitch viewport moves as necessary, and its five lines move with it rather
than disappearing above the screen. Pitch names identify every row, not just
line rows; C4 is bold when visible.

The cantus keeps its hollow circle (`○`, plain `o`) and the player keeps the
filled head (`●`, plain `*`). Colour alone distinguishes the given line more
strongly: saturated burnt-orange 130 against dark-blue 24, on parchment 230
with sparse 223 grain. Plain uses red 1 versus blue 4 on 7. No halo changes the
geometry or clears a bar boundary. The colour-contrast gate measures both rich
inks against 230, 223 and sounding yellow 222; all exceed 3:1. Console colours
are theme-dependent, so plain makes no exact RGB contrast claim.

The current bar is shaded (223 / plain 15); while hearing, that shade and the
caret move through all bars and both sounding heads light (222 / plain 11).
The legend names both inks below the staff. The first line of the right panel
is the bold blue **Editing bar N**. The separate **First break / at bar N**
section is the critic's finding, not a stale selection. The selected pitch and
listening position have their own lines. The hint starts with **h hear**.

At 80x24 the page is compact; 120x40 adds breathing room without stretching
pitch spacing. Notes outside a deliberately edited wide register are marked
with ^/v at the viewport edge instead of silently disappearing. Both tiers use
the same coordinates. Up/Down walk goldens assert every boundary in every frame.

## Names or a drawn clef

Pitch names are the default. The alternative cell-drawn spiral is a decorative art study,
not a treble-clef promise or a second input convention. Compare `tests/goldens/art/names-80-plain.txt`
and `clef-80-plain.txt`; the rich versions and both 120-column versions are
beside them. Names make the absolute pitch immediately readable on plain,
where the drawn clef is only a small spiral. C4 is distinguished with bold ink
when it is in the viewport. The names are therefore the recommended treatment.

Every golden has a companion `.sty` file: colour and attributes are part of the
image, not a promise inferred from an uncoloured text capture.

## Rhythm on the manuscript

Later books widen each bar to four cells per smallest unit and scroll by whole
bars. During listening the page follows the sounding event, not the last edited
note. Both voices share the supplied diatonic viewport; if their visible range
fits, neither is clipped simply to centre the player's pitch.

The shared bright cantus and blue player heads remain unchanged. Halves and
quarters gain stems, eighths a small flag, and the value row states /1, /2, /4
or /8 explicitly. Incoming ties form a shallow `\_/` arc below their heads,
continuing on both sides of a barline without erasing it. These marks use the
same ASCII geometry on both tiers. A rest is r. The interval row includes S or
w for strong/weak, its quality and its number; colour still describes harmonic
consonance, not whether a passing dissonance is legal in context.
