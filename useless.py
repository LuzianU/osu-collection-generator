from __future__ import annotations
from tqdm import tqdm
from timeslice import Note, Timeslice

def print_slice_as_beatmap(slice: Timeslice, reverse_holds=False) -> None:
    row: str = "│"
    for col in range(len(slice.notes)):
            if slice.notes[col] == Note.NOTE:
                    row += "═══│"
            elif slice.notes[col] == Note.HOLD:
                    row += "║ ║│"
            elif slice.notes[col] == Note.HOLD_END:
                    row += "╔═╗│" if reverse_holds else "╚═╝│"
            elif slice.notes[col] == Note.HOLD_START:
                    row += "╚═╝│" if reverse_holds else "╔═╗│"
            else:
                    row += "   │"
    row += "\tbpm={:6.2f}, time={:}".format(slice.bpm, slice.time)            
    
    if slice.weighted_count is not None:
        row += f", weighted_count={round(slice.weighted_count, 2)}"
    if slice.chordjack_weight is not None:
        row += f", chordjack_weight={round(slice.chordjack_weight, 2)}"
    
    tqdm.write(row)


def print_slices_as_beatmap(slices: list[Timeslice]) -> None:
    reversed = [x for x in slices]
    reversed.reverse()
    for slice in reversed:
        print_slice_as_beatmap(slice, reverse_holds=True)
