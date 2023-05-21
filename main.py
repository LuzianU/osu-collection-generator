from __future__ import annotations
import math
import sqlite3
from tqdm import tqdm
from osuclasses import Song, Collection
import controller as controller
from timeslice import Timeslice, Note
import songdb
import storagedb
import useless

OSU_DB_FILE: str = "C:\Games\osu!\osu!.db"
OSU_COLLECTION_FILE: str = "C:\Games\osu!\collection.db"
OSU_SONGS_FOLDER: str = "E:\Games\osu!\Songs"
# either change this to True or delte _gen_osu!.db to rescan original osu!.db
RESCAN_OSU_DB: bool = False

collection: Collection = Collection()
collection_baka: Collection = Collection()


def on_start() -> None:
    """
        use this method to read collection or initialize other variables
    """
    # collection.read(OSU_COLLECTION_FILE)
    collection_baka.read("uruha.db")


def songs_filter(song_info: Song.Info) -> bool:
    """ 
        specify if given song information should be kept in pool of songs
        song_info is what's available via osu!.db
        make sure to return True for songs to keep
    """

    # return song_info.gameplay_mode == 3 and song_info.md5_hash in collection.collections["🎹 LN"]  # only accept songs in collection
    # check if song is present in any collection
    # return any(song_info.md5_hash in md5s for md5s in collection_baka.collections.values())

    if song_info.gameplay_mode != 3:  # 3 is mania
        return False

    if song_info.circle_size != 7:  # filter out all non-7k
        return False

    if song_info.folder_name.startswith("- # IIDX 24 SINOBUZ"):
        return False

    if song_info.folder_name.startswith("[_BMS_]"):
        return False

    return True  # make sure to return True for all other songs


def songs_apply(encoded_song_data: str, song_info: Song.Info):
    """ 
        this method gets called for every song that got accepted by songs_filter
        song: Song = songdb.decode_to_song(encoded_song_data, song_info)
        to decode it
    """

    # use tqdm.write() instead of print() here qdm.write(song.info.song_title)

    # useless.print_slices_as_beatmap(slices[:10])

    # if "insert collection name here" not in collection.collections:
    #     collection.collections["insert collection name here"] = [] # create empty array if it doesn't exist yet
    # collection.collections["insert collection name here"].append(song.info.md5_hash) # add md5 to collection

    # tqdm.write(f"{song.info.song_title} [{song.info.difficulty}]")

    # 1:36 min without compression
    # 1:33 min with compression ???

    slices: list[Timeslice] = storagedb.select_object("slices", song_info.md5_hash, decompress=True)

    if slices is None:
        song: Song = songdb.decode_to_song(encoded_song_data, song_info)
        slices: list[Timeslice] = Timeslice.generate_timeslices(song)
        storagedb.insert_object("slices", song_info.md5_hash, slices, compress=True)

    column_count = song_info.circle_size

    if not slices:
        return

    if False:
        prev_slice = None
        for slice in slices:
            # [Note.NOTE, Note.EMPTY, Note.HOLD, Note.NOTE, Note.EMPTY, Note.NOTE, Note.NOTE] returns {0,3,5,6}
            slice.note_indices = {i for i, x in enumerate(slice.notes) if x == Note.NOTE}
            slice.weighted_count = 1 if len(slice.note_indices) >= 3 else 0
            slice.chordjack_weight = 0

            if prev_slice:  # skip first iteration
                intersection = slice.note_indices & prev_slice.note_indices  # set intersection -> overlapping notes
                sym_difference = slice.note_indices ^ prev_slice.note_indices  # set symmetric difference -> non-overlapping notes

                factor = 1 if len(intersection) > 0 and len(sym_difference) > 0 else 0
                slice.chordjack_weight = prev_slice.weighted_count * slice.weighted_count * factor

            prev_slice = slice
            # useless.print_slice_as_beatmap(slice)

    for slice in slices:
        # [Note.NOTE, Note.EMPTY, Note.HOLD, Note.NOTE, Note.EMPTY, Note.NOTE, Note.NOTE] returns {0,3,5,6}
        slice.note_indices = {i for i, x in enumerate(slice.notes) if x == Note.NOTE}
        slice.weighted_count = 1 if len(slice.note_indices) >= 2 else 0
        slice.chordjack_weight = 0

    for index, slice in enumerate(slices[:-1]):  # slices except last element
        next_slice = slices[index + 1]
        intersection = slice.note_indices & next_slice.note_indices  # set intersection -> overlapping notes

        if len(intersection) > 0:  # qualify as chordjack if at least one overlaps
            slice.chordjack_weight = slice.weighted_count

    avg = sum(map(lambda x: x.chordjack_weight, slices)) / len(slices)  # average of all chordjack_weights in slices

    key = round(avg, 1)

    # tqdm.write(f"{key} = {song_info.song_title} [{song_info.difficulty}]")

    if key < 1:
        key = str(key) + " - " + str(round(key+.1, 1))
    else:
        key = str(key)

    if key not in collection.collections:
        collection.collections[key] = []
    collection.collections[key].append(song_info.md5_hash)


def on_end() -> None:
    """ 
        use this to write collections to file
    """
    # collection.write(osu_collection_file) # OVERWRITE(!) collection file
    collection.write("collection.db")


if __name__ == "__main__":
    controller.start()
