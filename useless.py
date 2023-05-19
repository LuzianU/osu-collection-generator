from __future__ import annotations
from tqdm import tqdm
from timeslice import Note, Timeslice


def print_slices_as_beatmap(slices: list[Timeslice]) -> None:
    reversed = [x for x in slices]
    reversed.reverse()
    for slice in reversed:
        row: str = "│"
        for col in range(len(slice.notes)):
            if slice.notes[col] == Note.NOTE:
                    row += "═══│"
            elif slice.notes[col] == Note.HOLD:
                    row += "║ ║│"
            elif slice.notes[col] == Note.HOLD_END:
                    row += "╔═╗│"
            elif slice.notes[col] == Note.HOLD_START:
                    row += "╚═╝│"
            else:
                    row += "   │"
                    
        row += "\tbpm={:6.2f}, time={:}".format(slice.bpm, slice.time)
        tqdm.write(row)
