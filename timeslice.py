from __future__ import annotations
from collections import deque
import math
from osuclasses import Song
from enum import Enum


def _x_to_index(x: int, column_count: int) -> int:
    return max(0, min(math.floor(x * column_count / 512), column_count-1))


class Note(Enum):
    EMPTY, NOTE, HOLD_START, HOLD_END, HOLD = range(5)


class Timeslice:
    """A horizontal map slice containing time, current bpm and a list of which notes are present"""

    def __init__(self, time: int, column_count: int) -> None:
        self.notes: list[Note] = [Note.EMPTY for _ in range(column_count)]
        self.time: int = time
        self.bpm: int = 0

        self._has_hold_start: bool = False
        self._has_hold_end: bool = False

    def __eq__(self, other):
        return isinstance(other, Timeslice) and self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    def __hash__(self):
        return hash(self.time)

    def has_hold_start(self) -> bool:
        return self._has_hold_start

    def has_hold_end(self) -> bool:
        return self._has_hold_end

    def set_note(self, note: Note, column: int):
        self.notes[column] = note
        if note == Note.HOLD_START:
            self._has_hold_start = True
        elif note == Note.HOLD_END:
            self._has_hold_end = True

    @staticmethod
    def generate_timeslices(song: Song) -> list[Timeslice]:
        """generates a time-sorted list of Timeslices based on the given song"""

        timing_points: list[dict] = song.dict["TimingPoints"]
        hit_objects: list[dict] = song.dict["HitObjects"]
        column_count = song.info.circle_size

        hit_objects = sorted(hit_objects, key=lambda x: x["time"])

        slices: dict[int, Timeslice] = dict()
        end_slices: dict[int, Timeslice] = dict()

        def set_notes_for_slice(hit_object: dict, slice: Timeslice):
            type = hit_object["type"]
            col = _x_to_index(hit_object["x"], column_count)

            if type & (1 << 0):  # is note
                slice.set_note(Note.NOTE, col)
            elif type & (1 << 7):  # is hold
                slice.set_note(Note.HOLD_START, col)

                cres_end_time = int(hit_object['extras'].split(':')[0])

                match = end_slices.get(cres_end_time)

                if match:
                    match.set_note(Note.HOLD_END, col)
                else:
                    slice = Timeslice(cres_end_time, column_count)
                    slice.set_note(Note.HOLD_END, col)
                    end_slices[slice.time] = slice

        for hit_object in hit_objects:
            time: int = hit_object["time"]

            match = slices.get(time)

            if match:
                set_notes_for_slice(hit_object, match)
            else:
                slice: Timeslice = Timeslice(time, column_count)
                set_notes_for_slice(hit_object, slice)
                slices[time] = slice

        # adds the HOLD_ENDs to the slices. Depending on if the slice already exists it adds the HOLD_END or creates a new slice
        end_slices_key_set = set(end_slices.keys())
        for key in end_slices_key_set:
            end_slice = end_slices[key]
            if key in slices:
                slice = slices[key]
                for i in range(len(slice.notes)):
                    if end_slice.notes[i] == Note.HOLD_END:
                        slice.set_note(Note.HOLD_END, i)
            else:
                slices[key] = end_slice

        # sort by time
        slices = {k: slices[k] for k in sorted(slices)}
        timing_points: list[tuple[int, float]] = [(item["time"], item["beatLength"]) for item in timing_points]
        timing_points: deque[tuple[int, float]] = deque(
            sorted(timing_points, key=lambda tuple: tuple[0]))  # sort by time

        # set bpms for each slice based on timing_points
        current_bpm: int = 0
        for slice in slices.values():
            while timing_points and timing_points[0][0] <= slice.time:
                beatLength = timing_points.popleft()[1]
                if beatLength == 0:
                    current_bpm = 0
                else:
                    current_bpm = 60000 / beatLength

            slice.bpm = current_bpm
            last = slice

        # connect HOLD_STARTs with HOLD_ENDs by putting HOLD into every note array inbetween the start-end point
        items: list[Timeslice] = list(slices.values())
        for i in range(len(items)):
            slice: Timeslice = items[i]

            if not slice.has_hold_start():
                continue

            for col in range(len(slice.notes)):
                if slice.notes[col] != Note.HOLD_START:
                    continue

                for j in range(i+1, len(items)):
                    sub: Timeslice = items[j]
                    if sub.notes[col] == Note.HOLD_END:
                        break

                    sub.set_note(Note.HOLD, col)

        return items  # items is sorted by time
