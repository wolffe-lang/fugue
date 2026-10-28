# Keys

| Key | At the staff |
|---|---|
| Left / Right | Select the previous / next notated event, including rests |
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
A quit or interrupt never starts a page. The game negotiates kitty keyboard
flags 11 when the terminal answers its query, and falls back to legacy keys
otherwise. Press and repeat each perform one action; release performs none.
Shift arrows work on both paths.

`--mute` and `FUGUE_SOUND=0` suppress preparation and audio output, but not the
listening animation. `--plain` selects ASCII and the sixteen console colours.


Book I's persistent bottom hint begins `h hear   Space sound   Enter check`.
`h` begins at the first bar, regardless of the editing cursor, and plays both
voices through the last. The moving bar shade, caret and two lit heads show
what sounds. **Editing bar N** is the panel's first line; **Breaks: bar N** below it
lists only that bar's findings. A clean bar says **No break in this bar**.
The critic card after Enter still reports every bar and the global counts.
## Books II–V

At the title, 1–7 opens a book; b returns to that desk from a page or card.
Books I–VI start with three tutorials, then seeded pages. The seventh desk is
for your own cantus. Best stars per book
are saved in `.fugue-state`; set `FUGUE_STATE` to use another file. A corrupt or
unknown-format file is ignored, never interpreted as an answer.

Left and Right select one notated event at a time in every book, including
rests and tied notes. A held whole or half note is one position, not a row of
empty time slots. The caret marks that event's attack; the status gives its
onset and Up/Down changes that same event. A tie carries pitch edits through
the tied chain.

Books II–IV keep their species rhythm. In IV, t toggles an incoming barline
tie; in II and IV, 0 toggles the opening half rest.

Book V's bottom hint names its editable rhythm:

- `[` splits an event into equal halves, copying its pitch and rest state.
- `]` joins the next event in the same bar if their sum is one written value.
- `.` dots a quarter or half, borrowing its added time from the next event in
  that bar. It refuses by name if no valid value can remain. The bar stays full.
- `t` toggles a tie **to the next event**, copying pitch through its tie chain.
- `r` toggles the selected event between rest and note without changing its length.
- `u` undoes the complete edit, including durations, pitches and ties, and restores its selected event.

The final whole's value remains fixed. An editable rest or tie may be illegal:
the ordinary species judge reports it immediately rather than hiding the key.
Joins, splits and dots that cannot preserve a bar are refused by name.

The page owns its pitch range and whether rhythm is editable. Book VI's
integration uses the same keys for an editable countersubject, not its fixed
answer. Its `#` cycles natural → sharp → flat → natural anywhere; Books I–V
retain their cadence-only guard. All six books use event navigation.
`v` switches Book VI's writing desk.

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

A pitch above the visible register is marked `!`, not `^`; the
caret is reserved for selection. During listening, editing is locked and
the caret is the playhead.

## Book VII: your cantus

7 or `--book 7` opens a blank ten-whole line. `m` cycles the six modes without
transposing what you wrote. Left/Right selects a whole note; Up/Down writes it,
Shift-Up/Down moves an octave, Space sounds it, and h hears the one line.
`[` adds a whole at the end; `]` removes the selected whole. Undo restores
notes, length and selection together. The editor permits one to sixteen notes;
the critic requires eight to sixteen. The usual cadence-only # guard remains.
`v` chooses whether the subsequent counterpoint will be above or below.

Enter checks the melody with the same validator as the generator. Every break
has its bar, rule and tutor's explanation on the scrollable card. A legal card
shows the generator's exact shape score, summit penalty, ascent/descent counts
and interval-variety bonus. Enter again keeps that exact cantus and opens a
first-species exercise. Solve it with the usual editor and critic. Only the
solved pair earns the seventh book's stars; accepting the melody alone does not.
`r` edits again, `n` starts a fresh line, and b returns to the books. Mode/side
choices are not note edits and do not enter the note-undo history.

## Enhanced-path fixtures

The `enhanced-keys` pty row negotiates flags 11 and injects the kitty protocol
forms expected from Ghostty on macOS, in rich/plain at both sizes in all seven
books. These are protocol fixtures, **not a physical Ghostty capture**. A real
terminal capture is still needed to certify a particular Ghostty version.
The legacy pty rows remain the fallback proof.

Here ESC is byte 1b; `k` is 1 press, 2 repeat or 3 release:

| Control | Enhanced fixture bytes |
|---|---|
| Up/Down/Right/Left | `ESC [ 1 ; 1 : k A/B/C/D` |
| Shift-Up/Down | `ESC [ 1 ; 2 : k A/B` |
| Enter / Space / Escape | `ESC [ 13/32/27 ; 1 : k u` |
| # (Shift-3) | `ESC [ 51 ; 2 : k u` |
| h/u/n/r/q/b/v/m | `ESC [ 104/117/110/114/113/98/118/109 ; 1 : k u` |
| 0 and 1–7 | `ESC [ 48–55 ; 1 : k u` |
| [ / ] / . / t | `ESC [ 91/93/46/116 ; 1 : k u` |

The row holds Right through seven repeat events, then releases it: eight events,
eight selections, never a timer-driven ninth. Left returns by the same count.
Every action's first carrying frame is compared with its complete independent
headless state; releases must leave the frame unchanged and add no replay key.
The keyboard flag stack is popped before leaving the alternate screen.
