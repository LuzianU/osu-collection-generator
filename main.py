from __future__ import annotations
import math
import sqlite3
from tqdm import tqdm
from osuclasses import Song, Collection
import controller as controller
from timeslice import Timeslice, Note
import useless

OSU_DB_FILE: str = "C:\Games\osu!\osu!.db"
OSU_COLLECTION_FILE: str = "C:\Games\osu!\collection.db"
OSU_SONGS_FOLDER: str = "E:\Games\osu!\Songs"
# either change this to True or delte _gen_osu!.db to rescan original osu!.db
RESCAN_OSU_DB: bool = False

collection: Collection = Collection()


def on_start() -> None:
    """use this method to read collection or initialize other variables"""
    # collection.read(OSU_COLLECTION_FILE)
    collection.read("uruha.db")


def songs_filter(song_info: Song.Info) -> bool:
    """specify if given song information should be kept in pool of songs
       song_info is what's available via osu!.db
       make sure to return True for songs to keep"""

    return any(song_info.md5_hash in md5s for md5s in collection.collections.values())

    # return song_info.gameplay_mode == 3 and song_info.md5_hash in collection.collections["🎹 LN"]  # only accept songs in collection

    if song_info.gameplay_mode != 3:  # 3 is mania
        return False

    if song_info.circle_size != 7:  # filter out all non-7k
        return False

    if song_info.folder_name.startswith("- # IIDX 24 SINOBUZ"):
        return False

    if song_info.folder_name.startswith("[_BMS_]"):
        return False

    return True  # make sure to return True for all other songs


def songs_apply(song: Song):
    """this method gets called for every song that got accepted by songs_filter"""

    # use tqdm.write() instead of print() here qdm.write(song.info.song_title)

    # useless.print_slices_as_beatmap(slices[:10])

    # if "insert collection name here" not in collection.collections:
    #     collection.collections["insert collection name here"] = [] # create empty array if it doesn't exist yet
    # collection.collections["insert collection name here"].append(song.info.md5_hash) # add md5 to collection

    # tqdm.write(f"{song.info.song_title} [{song.info.difficulty}]")

    if song.info.song_title != "FAKE PROMISE":
        return

    slices: list[Timeslice] = Timeslice.generate_timeslices(song)
    column_count = song.info.circle_size

    def f(x, k=15):
        return math.exp(k * ((x/column_count) - 0.5)) / (math.exp(k * ((x/column_count) - 0.5)) + 1)

    for i, slice in enumerate(slices):
        # [Note.NOTE, Note.EMPTY, Note.HOLD, Note.HOLD_START, Note.EMPTY, Note.NOTE, Note.NOTE] returns {0,3,4,6}
        note_indices = set([i for i, x in enumerate(slice.notes) if x in [Note.NOTE, Note.HOLD_START, Note.HOLD_END]])
        weighted_count = f(len(note_indices))
        slice.weighted_count = weighted_count
        useless.print_slice_as_beatmap(slice)

    pass


def on_end() -> None:
    """use this to write collections to file"""
    # collection.write(osu_collection_file) # OVERWRITE(!) collection file


if __name__ == "__main__":
    controller.start()
