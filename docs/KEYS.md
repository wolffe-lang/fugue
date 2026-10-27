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
what sounds. **Editing bar N** is the panel's first line; **Breaks: bar N** below it
lists only that bar's findings. A clean bar says **No break in this bar**.
The critic card after Enter still reports every bar and the global counts.
## Books II–V

At the title, 1–6 opens a book; b returns to that desk from a page or card.
Each book starts with three tutorials, then seeded pages. Best stars per book
are saved in `.fugue-state`; set `FUGUE_STATE` to use another file. A corrupt or
unknown-format file is ignored, never interpreted as an answer.

Left and Right advance by the book's smallest unit: a half in II and IV, a
quarter in III, an eighth in V. The caret moves on every press, including inside a held note; Up and
Down change that complete note. The selected head identifies the held event,
while the caret marks its editable time offset. A tie carries pitch edits through the tied chain.

Books II–IV keep their species rhythm. In IV, t toggles an incoming barline
tie; in II and IV, 0 toggles the opening half rest.

Book V's bottom hint names its editable rhythm:

- `[` splits an event into equal halves, copying its pitch and rest state.
- `]` joins the next event in the same bar if their sum is one written value.
- `.` dots a quarter or half, borrowing its added time from the next event in
  that bar. It refuses by name if no valid value can remain. The bar stays full.
- `t` toggles a tie **to the next event**, copying pitch through its tie chain.
- `r` toggles the selected event between rest and note without changing its length.
- `u` undoes the complete edit, including durations, pitches, ties and cursor time.

The final whole's value remains fixed. An editable rest or tie may be illegal:
the ordinary species judge reports it immediately rather than hiding the key.
Joins, splits and dots that cannot preserve a bar are refused by name.

The page owns its pitch range and whether rhythm is editable. Book VI's
integration uses the same keys for an editable countersubject, not its fixed
answer. Its `#` cycles natural → sharp → flat → natural anywhere; Books I–V
retain their cadence-only guard. Books I–V keep their existing time-grid
navigation; Book VI selects notated events as described below. `v` switches
Book VI's writing desk.

## Book VI

6 opens the fugue book. Its first page edits the answer, its second edits the
countersubject, and its third and seeded pages use `v` to switch between both.
Switching keeps the notes but starts a fresh undo history on the new desk.
The answer must preserve the given rhythm; the critic names changes rather
than silently correcting them. `h` plays the whole exposition: subject alone,
then answer with countersubject. The end card follows three passed tutorials;
`n` then opens a seeded page and `b` shows the lit sixth book.

Book VI's pitch range is C3–C7. `#` cycles natural, sharp, flat and back to
natural anywhere in either written line; it is not restricted to a cadence.
The Answer desk keeps the subject's values fixed. The Countersubject desk
uses Book V's `[`, `]`, `.`, `t` and `r` rhythm controls. Every change is judged
against the moving answer in both octave dispositions.

In Book VI, Left and Right select the previous or next notated event in the
voice you are writing. Up and Down change that event; a tied chain still changes
together. A held note is one selection, not several empty time slots. The single
caret stays at that event’s column, and the status names its onset. Book VI keeps
Editing bar and bar/beat at the
top of the same status column as the other books; named findings below belong
only to that bar. Both writing desks number their local bars from one. During
listening, the exposition's second entry follows the subject's six bars.

A Book VI pitch outside the visible register is marked `!`, not `^`; the
caret is reserved for selection. During listening, editing is locked and
the caret is the playhead.
