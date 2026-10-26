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
