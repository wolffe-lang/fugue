# Keys

| Key | At the staff |
|---|---|
| Left / Right | Select a bar |
| Up / Down | Raise / lower its note one diatonic step and audition it |
| Shift-Up / Shift-Down | Raise / lower one octave and audition |
| # | Toggle the raised leading tone, only at the permitted cadence position |
| Space | Sound the selected note |
| h | Hear both voices; edits wait until the pass ends |
| Enter | Open the critic's card |
| u | Undo one note edit, returning to its bar |
| n | Turn to the next tutorial or seeded page |
| q / Escape | Quit from every screen |

Enter or any mapped non-quit key opens the title. On the critic's card, r
returns to editing, n turns the page, Up/Down scroll the findings, and q leaves.
A quit or interrupt never starts a page. Shift arrows use the terminal's legacy
CSI modifier form; the pinned engine does not yet decode CSI-u forms.

`--mute` and `FUGUE_SOUND=0` suppress preparation and audio output, but not the
listening animation. `--plain` selects ASCII and the sixteen console colours.


Book I's persistent bottom hint begins `h hear   Space sound   Enter check`.
`h` begins at the first bar, regardless of the editing cursor, and plays both
voices through the last. The moving bar shade, caret and two lit heads show
what sounds. **Editing bar N** is the panel's first line; **First break** below
it names a critic finding, which need not change when the cursor moves.
## Books II–V

At the title, 1–5 opens a book; b returns to that desk from a page or card.
Each book starts with three tutorials, then seeded pages. Best stars per book
are saved in `.fugue-state`; set `FUGUE_STATE` to use another file. A corrupt or
unknown-format file is ignored, never interpreted as an answer.

Left and Right advance by the book's smallest unit: a half in II and IV, a
quarter in III, an eighth in V. The cursor can stand inside a held note; Up and
Down change that complete note. A tie carries pitch edits through the tied chain.

- t adds or removes an incoming tie at a barline in IV or V.
- 0 adds or removes the opening half rest in II, IV or V.
- ] splits a note in half in V; [ joins equal adjacent values in the same bar.
- u undoes pitch, rest, tie and value edits, including the previous cursor place.
- The final whole is fixed. Rhythm edits that would cross a barline are refused.
- In Aeolian's final three attacks, # can raise the sixth before the raised
  seventh; the critic accepts that sixth only in the complete ascending cadence.
